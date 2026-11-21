from pathlib import Path
from datetime import date, timedelta
from flask import Flask, jsonify, render_template, request
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / 'data' / 'marketing.csv'
if not DATA_FILE.exists():
    from generate_data import generate
    generate()

DF = pd.read_csv(DATA_FILE, parse_dates=['date'])
app = Flask(__name__)
FIELDS = ['impressions', 'clicks', 'video_views', 'conversions', 'spend', 'revenue']

def totals(frame):
    sums = frame[FIELDS].sum()
    impressions = int(sums['impressions'])
    clicks = int(sums['clicks'])
    conversions = int(sums['conversions'])
    spend = float(sums['spend'])
    return {
        'impressions': impressions, 'clicks': clicks,
        'video_views': int(sums['video_views']), 'conversions': conversions,
        'spend': round(spend, 2), 'revenue': round(float(sums['revenue']), 2),
        'ctr': (100 * clicks / impressions) if impressions else None,
        'cpm': (1000 * spend / impressions) if impressions else None,
        'cpc': (spend / clicks) if clicks else None,
        'conversion_rate': (100 * conversions / clicks) if clicks else None,
    }

def subset(start, end, channel, source, campaign):
    mask = (DF['date'] >= pd.Timestamp(start)) & (DF['date'] <= pd.Timestamp(end))
    for col, val in [('channel', channel), ('source', source), ('campaign', campaign)]:
        if val and val != 'All':
            mask &= DF[col].eq(val)
    return DF.loc[mask]

def delta(current, previous):
    if current is None or previous is None or previous == 0:
        return None
    return round((current / previous - 1) * 100, 2)

def grouped(frame, key, previous):
    records = []
    for name, f in frame.groupby(key, sort=False):
        now = totals(f)
        old = totals(previous[previous[key] == name])
        records.append({'name': name, **now,
                        'impressions_change': delta(now['impressions'], old['impressions']),
                        'ctr_change': delta(now['ctr'], old['ctr'])})
    return sorted(records, key=lambda x: x['impressions'], reverse=True)

def series(frame, frequency):
    if frame.empty:
        return []
    d = frame.copy()
    d['period'] = d['date'].dt.to_period(frequency).dt.to_timestamp()
    aggregated = d.groupby(['period', 'channel'], as_index=False)[FIELDS].sum()
    return [{'period': r['period'].strftime('%Y-%m-%d'), 'channel': r['channel'],
             **totals(aggregated.iloc[[idx]])}
            for idx, r in aggregated.iterrows()]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/options')
def options():
    return jsonify({k: sorted(DF[k].unique().tolist()) for k in ['channel', 'source', 'campaign']})

@app.route('/api/dashboard')
def dashboard():
    start = request.args.get('start', '2023-01-01')
    end = request.args.get('end', '2023-12-31')
    channel = request.args.get('channel', 'All')
    source = request.args.get('source', 'All')
    campaign = request.args.get('campaign', 'All')
    try:
        a, b = date.fromisoformat(start), date.fromisoformat(end)
    except ValueError:
        return jsonify({'error': 'Invalid ISO dates (YYYY-MM-DD)'}), 400
    if a > b or (b - a).days > 731:
        return jsonify({'error': 'Invalid date range'}), 400
    current = subset(a, b, channel, source, campaign)
    # Calendar-aligned previous year for true year-over-year comparisons.
    try:
        old_a = a.replace(year=a.year - 1)
        old_b = b.replace(year=b.year - 1)
    except ValueError:
        return jsonify({'error': 'Leap-day comparison unsupported; adjust the date range'}), 400
    previous = subset(old_a, old_b, channel, source, campaign)
    now = totals(current)
    before = totals(previous)
    freq = 'D' if (b - a).days <= 45 else 'W' if (b - a).days <= 150 else 'M'
    trends = series(current, freq)
    return jsonify({
        'kpis': {key: {'value': value, 'change': delta(value, before[key])} for key, value in now.items()},
        'channels': grouped(current, 'channel', previous),
        'sources': grouped(current, 'source', previous),
        'campaigns': grouped(current, 'campaign', previous),
        'trends': trends,
        'period': {'start': start, 'end': end, 'comparison_start': old_a.isoformat(), 'comparison_end': old_b.isoformat()},
        'rows': int(len(current)), 'synthetic': True,
    })

if __name__ == '__main__':
    app.run(debug=True)
