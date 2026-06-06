"""
QuestionEngine — Deterministic domain routing and probability synthesis.

Architecture:
    Question (str)
        ↓
    Domain Router (keyword matching)
        ↓
    Domain natal promise score (from NatalPromiseEngine output)
        ↓
    MasterProbabilityEngine re-evaluated with domain-specific natal score
        ↓
    Structured answer: probability, grade, timing_confidence, domain

Rules:
    - Zero AI/ML. Pure keyword lookup for routing.
    - Domain routing is keyword-prefix, not semantic matching.
    - If no domain match: returns multi-domain summary (generic answer).
    - MasterProbabilityEngine is called with domain natal promise replacing
      the all-domain average used in the pipeline default.
"""
from app.config.astrology_constants import NATAL_PROMISE_GRADES, PROBABILITY_GRADES
from app.engines.master_probability_engine import MasterProbabilityEngine
from app.utils.astrology_math import clamp_score


# ---------------------------------------------------------------------------
# Domain Keyword Routing Table
# ---------------------------------------------------------------------------
# Each domain maps to a list of trigger keywords (lowercased).
# Matching: any keyword found as a whole word or substring in the question.
# Priority: first matched domain in DOMAIN_PRIORITY wins.

DOMAIN_KEYWORDS = {
    "marriage":    [
        "marriage", "married", "wedding", "spouse", "husband", "wife",
        "partner", "love", "relationship", "divorce", "remarriage", "second marriage"
    ],
    "career":      [
        "career", "job", "profession", "work", "business", "promotion",
        "employment", "office", "salary", "transfer",
        "foreign job", "government job", "service"
    ],
    "wealth":      [
        "wealth", "money", "finance", "rich", "income", "earn",
        "financial", "investment", "profit", "loss", "debt", "loan",
        "lottery", "inheritance", "windfall"
    ],
    "education":   [
        "education", "study abroad", "study", "school", "college", "university",
        "degree", "learning", "knowledge", "exam", "course", "graduate",
        "higher education", "academic"
    ],
    "children":    [
        "children", "child", "baby", "son", "daughter", "pregnancy",
        "offspring", "progeny", "birth", "kid", "kids", "parent", "parenthood"
    ],
    "property":    [
        "property", "house", "home", "land", "real estate", "apartment",
        "flat", "plot", "building", "construction", "own house"
    ],
    "health":      [
        "health", "illness", "disease", "medical", "sick", "wellness",
        "body", "surgery", "hospital", "accident", "injury", "recover",
        "longevity", "chronic"
    ],
    "spirituality":[
        "spiritual", "religion", "dharma", "moksha", "meditation",
        "yoga", "divine", "pilgrimage", "temple", "renunciation"
    ],
}

# Priority order: first match wins when multiple domains could match
DOMAIN_PRIORITY = [
    "marriage", "career", "wealth", "children", "education",
    "property", "health", "spirituality"
]


class QuestionEngine:
    """
    Deterministic question router and probability synthesiser.

    Usage:
        engine = QuestionEngine()
        answer = engine.answer(
            question="Will I get married?",
            pipeline_output=runner.process(raw_data)
        )

    Returns a structured answer dict with domain, probability score, grade,
    natal promise, dasha confidence, and supporting evidence.
    """

    def __init__(self):
        self.keywords        = DOMAIN_KEYWORDS
        self.priority        = DOMAIN_PRIORITY
        self.master_engine   = MasterProbabilityEngine()
        self.promise_grades  = NATAL_PROMISE_GRADES

    # -------------------------------------------------------------------------
    # Public Interface
    # -------------------------------------------------------------------------

    def answer(self, question: str, pipeline_output: dict) -> dict:
        """
        Routes the question to a domain and computes domain-specific probability.

        Args:
            question (str): Free-text question from the user.
            pipeline_output (dict): Full PipelineRunner.process() output.

        Returns:
            dict: Structured answer with probability, grade, domain breakdown.
        """
        engine_outputs = pipeline_output.get("engine_outputs", {})
        natal_results  = engine_outputs.get("natal_promise", {})

        # Step 1: Route to domain
        domain = self._route(question)

        # Step 2: Extract domain-specific natal promise score
        if domain and domain in natal_results:
            natal_score = natal_results[domain].get("score", 50)
            natal_data  = natal_results[domain]
            routed      = True
        else:
            # Generic fallback: average of all domains
            natal_score = self._average_natal(natal_results)
            natal_data  = {}
            domain      = None
            routed      = False

        # Step 3: Re-evaluate master probability with domain natal score
        probability = self._domain_probability(
            natal_score, engine_outputs
        )

        # Step 4: Extract dasha and AV timing evidence
        timing = self._timing_evidence(engine_outputs)

        # Step 5: Assemble answer
        return {
            "question":      question,
            "domain":        domain,
            "routed":        routed,
            "probability": {
                "score": probability["final_score"],
                "grade": probability["grade"],
                "raw":   probability["raw_score"],
            },
            "natal_promise": {
                "score":    natal_score,
                "promise":  self._promise_grade(natal_score),
                "karaka":   natal_data.get("karaka", ""),
                "afflictions": natal_data.get("afflictions", []),
            },
            "timing": timing,
            "factor_breakdown": probability.get("breakdown", {}),
            "answer_text": self._compose_answer(
                question, domain, natal_score, probability, timing, routed
            ),
        }

    def route_domain(self, question: str) -> str | None:
        """Public accessor for domain routing (useful for testing)."""
        return self._route(question)

    # -------------------------------------------------------------------------
    # Domain Routing
    # -------------------------------------------------------------------------

    def _route(self, question: str) -> str | None:
        """
        Keyword-based domain routing.
        Scans the question (lowercased) for each domain's keywords.
        Returns the first matched domain in DOMAIN_PRIORITY order.
        Returns None if no domain matches.
        """
        q = question.lower().strip()
        for domain in self.priority:
            for keyword in self.keywords[domain]:
                if keyword in q:
                    return domain
        return None

    # -------------------------------------------------------------------------
    # Domain Probability
    # -------------------------------------------------------------------------

    def _domain_probability(
        self,
        natal_score:    float,
        engine_outputs: dict,
    ) -> dict:
        """
        Re-evaluates MasterProbabilityEngine with the domain-specific natal score
        replacing the pipeline's all-domain average.

        Injects natal_score as a synthetic single-domain natal_promise entry
        so MasterProbabilityEngine reads it via _natal_promise().
        """
        # Build a synthetic natal_promise dict with only the domain score
        synthetic_natal = {"__domain__": {"score": natal_score}}

        # Merge into a copy of engine_outputs so we don't mutate the pipeline output
        domain_outputs = dict(engine_outputs)
        domain_outputs["natal_promise"] = synthetic_natal

        return self.master_engine.evaluate(domain_outputs)

    def _average_natal(self, natal_results: dict) -> float:
        """Fallback: average of all domain natal scores."""
        if not natal_results:
            return 50.0
        scores = [d["score"] for d in natal_results.values()
                  if isinstance(d, dict) and "score" in d]
        return round(sum(scores) / len(scores), 2) if scores else 50.0

    # -------------------------------------------------------------------------
    # Timing Evidence
    # -------------------------------------------------------------------------

    def _timing_evidence(self, engine_outputs: dict) -> dict:
        """
        Extracts dasha timing confidence from dasha_results.
        Returns a compact timing summary for the answer.
        """
        dasha_results = engine_outputs.get("dashas", {})
        av_results    = engine_outputs.get("ashtakavarga", {})

        md_lord, md_mult = "", 1.0
        ad_lord, ad_mult = "", 1.0

        for lord, data in dasha_results.items():
            temporal = data.get("temporal_activation", {})
            flags    = data.get("confidence_flags", [])
            if "active_mahadasha" in flags:
                md_lord = lord
                md_mult = temporal.get("timing_multiplier", 1.0)
            elif "active_antardasha" in flags:
                ad_lord = lord
                ad_mult = temporal.get("timing_multiplier", 1.0)

        db_support  = av_results.get("dasha_bav_support", {})
        confidence  = db_support.get("timing_confidence", "unknown")
        bav_mult    = db_support.get("timing_confidence_multiplier", 1.0)

        return {
            "mahadasha":            md_lord,
            "mahadasha_multiplier": md_mult,
            "antardasha":           ad_lord,
            "antardasha_multiplier": ad_mult,
            "bav_timing_confidence": confidence,
            "bav_multiplier":        bav_mult,
            "activation_level":      self._activation_label(md_mult),
        }

    @staticmethod
    def _activation_label(multiplier: float) -> str:
        """Maps timing_multiplier to a human-readable activation level."""
        if multiplier >= 1.20:  return "HIGH"
        if multiplier >= 1.10:  return "MODERATE"
        if multiplier >= 1.00:  return "NEUTRAL"
        return "SUPPRESSED"

    # -------------------------------------------------------------------------
    # Answer Composition
    # -------------------------------------------------------------------------

    def _compose_answer(
        self,
        question:    str,
        domain:      str | None,
        natal_score: float,
        probability: dict,
        timing:      dict,
        routed:      bool,
    ) -> str:
        """
        Composes a deterministic one-paragraph answer text.
        No generative AI. Template-based from scored components.
        """
        prob_score = probability["final_score"]
        prob_grade = probability["grade"]
        promise    = self._promise_grade(natal_score)
        md         = timing.get("mahadasha", "unknown").capitalize()
        ad         = timing.get("antardasha", "unknown").capitalize()
        activation = timing.get("activation_level", "NEUTRAL")
        bav_conf   = timing.get("bav_timing_confidence", "unknown").upper()

        if not routed:
            return (
                f"Domain could not be determined from: '{question}'. "
                f"General probability: {prob_score}/100 ({prob_grade}). "
                f"Active dasha: {md} MD / {ad} AD."
            )

        domain_label = domain.capitalize()
        lines = [
            f"{domain_label} promise from natal chart: {natal_score}/100 ({promise}).",
            f"Combined probability: {prob_score}/100 ({prob_grade}).",
            f"Active dasha: {md} Mahadasha / {ad} Antardasha.",
            f"Dasha activation: {activation} (timing multiplier: "
            f"{timing.get('mahadasha_multiplier', 1.0):.2f}).",
            f"Ashtakavarga timing confidence: {bav_conf}.",
        ]
        return " ".join(lines)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _promise_grade(self, score: float) -> str:
        """4-tier promise classification."""
        for threshold, label in self.promise_grades:
            if score >= threshold:
                return label
        return "PRESENT"
