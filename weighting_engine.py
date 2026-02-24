class WeightingEngine:

    def combine(self, ai_conf, doc_conf, fact_conf):
        return (
            ai_conf * 0.4 +
            doc_conf * 0.4 +
            fact_conf * 0.2
        )
