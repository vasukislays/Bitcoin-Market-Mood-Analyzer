import pandas as pd

trades = pd.read_csv(r"C:\Users\Samee\Downloads\historical_data.csv")
sentiment = pd.read_csv(r"C:\Users\Samee\Downloads\fear_greed_index.csv")

print(trades.columns.tolist())
print(sentiment.columns.tolist())

trades['Timestamp IST'] = pd.to_datetime(trades['Timestamp IST'])
trades['date'] = trades['Timestamp IST'].dt.date

sentiment['date'] = pd.to_datetime(sentiment['date'])
sentiment['date'] = sentiment['date'].dt.date

merged = pd.merge(
    trades,
    sentiment[['date', 'classification']],
    on='date',
    how='inner'
)

print("Merged Dataset Shape:", merged.shape)

sentiment_stats = merged.groupby('classification').agg(
    Total_Trades=('Closed PnL', 'count'),
    Total_PnL=('Closed PnL', 'sum'),
    Average_PnL=('Closed PnL', 'mean'),
    Median_PnL=('Closed PnL', 'median')
).sort_values('Total_PnL', ascending=False)

print("\nSentiment Performance")
print(sentiment_stats)

side_analysis = merged.groupby(
    ['classification', 'Side']
)['Closed PnL'].agg(['count', 'sum', 'mean'])

print("\nBuy/Sell Analysis")
print(side_analysis)

merged['Win'] = merged['Closed PnL'] > 0

win_rates = merged.groupby(
    'classification'
)['Win'].mean() * 100

print("\nWin Rates (%)")
print(win_rates)

trader_performance = merged.groupby(
    ['Account', 'classification']
)['Closed PnL'].sum().reset_index()

top_traders = trader_performance.groupby(
    'Account'
)['Closed PnL'].sum().sort_values(
    ascending=False
).head(10)

print("\nTop 10 Traders")
print(top_traders)

risk_stats = merged.groupby('classification').agg(
    PnL_STD=('Closed PnL', 'std'),
    PnL_MIN=('Closed PnL', 'min'),
    PnL_MAX=('Closed PnL', 'max')
)

print("\nRisk Statistics")
print(risk_stats)

with pd.ExcelWriter("analysis_results.xlsx") as writer:
    sentiment_stats.to_excel(writer, sheet_name="Sentiment")
    side_analysis.to_excel(writer, sheet_name="BuySell")
    win_rates.to_frame("WinRate").to_excel(writer, sheet_name="WinRates")
    trader_performance.to_excel(writer, sheet_name="TraderPerformance", index=False)
    risk_stats.to_excel(writer, sheet_name="RiskStats")

print("\nAnalysis completed successfully!")
print("Results saved to analysis_results.xlsx")

import matplotlib.pyplot as plt

sentiment_stats['Total_PnL'].plot(
    kind='bar',
    figsize=(8, 5),
    title='Total PnL by Market Sentiment'
)

plt.ylabel('PnL')
plt.tight_layout()
plt.show()