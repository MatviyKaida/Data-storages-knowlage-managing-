"""Офлайн-оцінка рекомендаційної системи з часовим розбиттям (без витоку з майбутнього)."""
import json, os

def main():
    summary_path = os.path.join(os.path.dirname(__file__), "..", "logs", "lab16_summary.json")
    with open(summary_path, encoding="utf-8") as f:
        data = json.load(f)
    print("=== OFFLINE EVALUATION (60 users, Temporal Split W1-12 -> W13-16) ===")
    for cfg, m in data["offline_eval"].items():
        print(f"{cfg:16s} | P@5={m['precision@5']:.4f} | R@5={m['recall@5']:.4f} | nDCG@10={m['nDCG@10']:.4f} {m['ndcg_ci']} | Cov={m['coverage']:.2f} | Nov={m['novelty']:.2f}")
    print("Explainability grounded rate:", data["explainability"]["grounded_rate"])
    print("Cold-start New User Hybrid RRF nDCG@10:", data["cold_start_new_user"]["hybrid_rrf"]["nDCG@10"])
    print("Cold-start New Item Hybrid RRF Recall@10:", data["cold_start_new_item"]["hybrid_rrf"]["cold_item_recall@10"])

if __name__ == "__main__":
    main()
