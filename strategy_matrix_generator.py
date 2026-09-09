import sqlite3
import os
import json

base_dir = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
db_path = os.path.join(base_dir, 'phantomx_knowledge.db')
output_dir = os.path.join(base_dir, 'blockchain_strategy_matrices')

def generate_matrices():
    print("--- PHANTOMX MATRIX GENERATOR: ZERO GAP EXECUTION ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT chain_id, name, is_defi_active, tvl, knowledge_status FROM chains")
    chains = cursor.fetchall()
    
    total_generated = 0
    
    for chain in chains:
        cid = chain[0]
        cname = str(chain[1]).replace(" ", "_").replace("/", "_").replace("\\", "_")
        cstatus = chain[4]
        
        md_content = f"# PhantomX Strategy Matrix: {chain[1]} (Chain ID: {cid})\n\n"
        md_content += f"**Status:** {cstatus}\n**DeFi Active:** {'Yes' if chain[2] else 'No'}\n**TVL:** ${chain[3]:,.2f}\n\n"
        
        cursor.execute("SELECT protocol_id, name FROM protocols WHERE chain_id=?", (cid,))
        dexs = cursor.fetchall()
        
        cursor.execute("SELECT pool_name, tvl FROM pools WHERE dex_protocol_id IN (SELECT protocol_id FROM protocols WHERE chain_id=?) ORDER BY tvl DESC", (cid,))
        pools = cursor.fetchall()
        
        cursor.execute("SELECT provider_id, name FROM flash_loan_providers WHERE chain_id=?", (cid,))
        providers = cursor.fetchall()
        
        applicable_strategies = []
        
        # 1. Spatial Arbitrage
        if len(dexs) >= 2:
            applicable_strategies.append("- `[x]` **DEX Spatial Arbitrage** (Buy low on DEX A, sell high on DEX B)")
        else:
            applicable_strategies.append("- `[ ]` DEX Spatial Arbitrage (Requires >= 2 DEXs)")
            
        # 2. Triangular Arbitrage
        if len(pools) >= 3:
             applicable_strategies.append("- `[x]` **Triangular Arbitrage** (Path: A -> B -> C -> A on the same DEX)")
        else:
             applicable_strategies.append("- `[ ]` Triangular Arbitrage (Requires >= 3 pools)")
             
        # 3. Liquidations & Collateral Swaps
        has_lending = any("aave" in p[1].lower() or "maker" in p[1].lower() or "compound" in p[1].lower() for p in providers)
        if has_lending:
            applicable_strategies.append("- `[x]` **Liquidations** (Trigger underwater CDPs)")
            applicable_strategies.append("- `[x]` **Collateral Swaps** (Swap collateral assets without closing positions)")
            applicable_strategies.append("- `[x]` **Interest Rate Arbitrage** (Borrow low, lend high across protocols)")
        else:
            applicable_strategies.append("- `[ ]` Liquidations (Requires Lending protocol)")
            applicable_strategies.append("- `[ ]` Collateral Swaps (Requires Lending protocol)")
            applicable_strategies.append("- `[ ]` Interest Rate Arbitrage (Requires Lending protocol)")
            
        # Write Strategies
        md_content += "## Applicable Master Strategies\n"
        md_content += "\n".join(applicable_strategies) + "\n\n"
        
        # Write Flash Providers
        md_content += f"## Flash Loan Providers ({len(providers)})\n"
        for p in providers:
            md_content += f"- {p[1]} (ID: {p[0]})\n"
        if not providers:
            md_content += "*None detected locally.*\n"
        md_content += "\n"
        
        # Write DEXs
        md_content += f"## Mapped DEXs ({len(dexs)})\n"
        for d in dexs:
            md_content += f"- {d[1]} (ID: {d[0]})\n"
        if not dexs:
            md_content += "*None detected locally.*\n"
        md_content += "\n"
        
        # Write Pools - NO TRUNCATION (Zero Gap Policy)
        md_content += f"## Liquidity Pools / Pairs ({len(pools)})\n"
        for p in pools:
             md_content += f"- {p[0]} (TVL: ${p[1]:,.2f})\n"
        if not pools:
            md_content += "*None detected locally.*\n"
            
        filename = f"chain_{cid}_{cname}_strategy.md"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        total_generated += 1
        
    conn.close()
    print(f"Zero Gap Matrix Generation Complete. Overwritten {total_generated} strategy files with fully saturated pool lists.")

if __name__ == "__main__":
    generate_matrices()
