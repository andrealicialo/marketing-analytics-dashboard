"""Reproducible, explicitly synthetic, daily marketing data for 2022-2023."""
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT = Path(__file__).parent / 'data' / 'marketing.csv'
SEED = 2026
SOURCES = {
    'Programmatic': ['Amazon Ad Server', 'StackAdapt', 'Google Display & Video 360'],
    'Paid Search': ['Google Search Ads 360', 'Bing Ads'],
    'Paid Social': ['Facebook', 'LinkedIn Ads'],
    'Organic': ['Google Organic', 'Organic Social'],
}
CAMPAIGNS = ['Brand Awareness', 'Audience Expansion', 'Product Launch', 'Always-on Acquisition']
CHANNELS = {
    'Programmatic': dict(budget=1800, cpm=12, ctr=0.0105, cvr=0.026, video=0.55),
    'Paid Search': dict(budget=1450, cpm=35, ctr=0.0550, cvr=0.072, video=0.02),
    'Paid Social': dict(budget=850, cpm=11, ctr=0.0170, cvr=0.032, video=0.42),
    'Organic': dict(budget=0, cpm=0, ctr=0.0680, cvr=0.049, video=0.08),
}

def generate():
    rng = np.random.default_rng(SEED)
    rows = []
    dates = pd.date_range('2022-01-01', '2023-12-31', freq='D')
    for date in dates:
        day = (date - dates[0]).days
        season = 1 + 0.16 * np.sin(2 * np.pi * day / 365.25) + (0.20 if date.month in [11, 12] else 0)
        year_factor = 1.16 if date.year == 2023 else 1.0
        for channel, cfg in CHANNELS.items():
            for source in SOURCES[channel]:
                for campaign in CAMPAIGNS:
                    shift = (0.86 if campaign == 'Brand Awareness' else 1.10 if campaign == 'Always-on Acquisition' else 1)
                    multiplier = rng.lognormal(0, 0.20) * season * shift * year_factor
                    if channel == 'Organic':
                        impressions = int(max(0, rng.normal(36000, 4200) * multiplier))
                        spend = 0.0  # Paid-media spend only; organic traffic has no attributed paid spend
                    else:
                        target_spend = cfg['budget'] / (len(SOURCES[channel]) * len(CAMPAIGNS))
                        spend = round(max(10, target_spend * multiplier), 2)
                        impressions = int(round(spend / (cfg['cpm'] * rng.uniform(0.88, 1.12)) * 1000))
                    ctr = float(np.clip(cfg['ctr'] * rng.lognormal(0, 0.16), 0.001, 0.25))
                    clicks = int(rng.binomial(impressions, ctr))
                    cvr = float(np.clip(cfg['cvr'] * rng.lognormal(0, 0.18), 0.001, 0.40))
                    conversions = int(rng.binomial(clicks, cvr))
                    views = int(rng.binomial(impressions, cfg['video'] * rng.uniform(0.7, 0.95)))
                    revenue = round(conversions * rng.uniform(60, 145), 2)
                    rows.append((date.date().isoformat(), channel, source, campaign,
                                 impressions, clicks, views, conversions, spend, revenue))
    df = pd.DataFrame(rows, columns=['date', 'channel', 'source', 'campaign',
                                      'impressions', 'clicks', 'video_views', 'conversions', 'spend', 'revenue'])
    OUTPUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f'Generated {len(df):,} rows in {OUTPUT}')

if __name__ == '__main__':
    generate()
