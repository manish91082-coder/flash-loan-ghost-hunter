import json, sys
sys.path.insert(0, '.')
from live_price_fetcher import get_live_price_snapshot
from live_spread_analyzer import analyze_v2_opportunity, estimate_gas_cost_usd, compute_optimal_loan

snap = get_live_price_snapshot('WETH')
gas = snap.get('gas_gwei_live', 30.0)
univ3 = snap['univ3'].get('price_usd')
quickv2 = snap['quickv2'].get('price_usd')

print("WETH Debug:")
print("  UniV3:   $" + str(round(univ3, 4) if univ3 else "N/A"))
print("  QuickV2: $" + str(round(quickv2, 4) if quickv2 else "N/A"))
print("  Gas Gwei: " + str(gas))

matic_p = 0.0987
gas_usd = estimate_gas_cost_usd(gas, matic_p)
print("  Gas cost USD: $" + str(round(gas_usd, 4)))

# What loan would we need to be profitable?
# net_profit = loan * spread - loan * fee - gas
# loan * (spread - fee) = min_profit + gas
# loan = (min_profit + gas) / (spread - fee)
spread_d = abs(univ3 - quickv2) / min(univ3, quickv2)
fee_d = 0.0005  # Permutation A fee
eff_spread = spread_d - fee_d
print("  Spread (decimal): " + str(round(spread_d, 6)))
print("  Effective spread after fee: " + str(round(eff_spread, 6)))
if eff_spread > 0:
    min_loan = (0.50 + gas_usd) / eff_spread
    print("  Min loan for $0.50 profit: $" + str(round(min_loan, 2)))
    max_loan = 50000
    print("  Max configured loan: $" + str(max_loan))
    optimal = compute_optimal_loan('WETH', spread_d * 100, gas_usd)
    print("  Computed optimal loan: $" + str(optimal))
    
    gross = optimal * spread_d
    friction = optimal * fee_d
    net = gross - friction - gas_usd
    print("  Gross: $" + str(round(gross, 4)))
    print("  Friction: $" + str(round(friction, 4)))
    print("  Net profit: $" + str(round(net, 4)))

result = analyze_v2_opportunity('WETH', snap)
print()
print("V2 Analysis Result:")
print("  Action: " + str(result.get("action")))
print("  Spread: " + str(result.get("spread_pct")) + "%")
print("  Perm: " + str(result.get("selected_permutation")))
print("  Loan: $" + str(result.get("optimal_loan_usd")))
print("  Net: $" + str(result.get("net_profit_usd")))
print("  Reason: " + str(result.get("decision_reason")))
