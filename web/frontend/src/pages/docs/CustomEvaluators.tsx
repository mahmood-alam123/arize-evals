export default function CustomEvaluators() {
  return (
    <div className="docs-content">
      <h1>Custom Evaluators</h1>

      <p>
        While Company Eval provides built-in evaluation suites, you may need custom
        evaluators for domain-specific metrics.
      </p>

      <div className="card p-4 my-6 border-yellow-500/30 bg-yellow-500/5">
        <p className="text-yellow-400 font-medium mb-2">Coming Soon</p>
        <p className="text-white/70 mb-0">
          Custom evaluator support is on the roadmap. This page previews the planned API.
        </p>
      </div>

      <h2>Planned API</h2>

      <h3>Python Function Evaluator</h3>

      <pre><code>{`# my_app/evaluators.py
from company_eval_framework import Evaluator

class DomainAccuracyEvaluator(Evaluator):
    name = "domain_accuracy"

    def evaluate(self, input: str, output: str, context: str = None) -> float:
        """
        Return 1.0 if output is accurate, 0.0 otherwise.
        """
        # Your custom logic here
        if "correct answer" in output.lower():
            return 1.0
        return 0.0`}</code></pre>

      <h3>LLM-Based Custom Evaluator</h3>

      <pre><code>{`# my_app/evaluators.py
from company_eval_framework import LLMEvaluator

class BrandVoiceEvaluator(LLMEvaluator):
    name = "brand_voice"

    prompt = """
    Evaluate if the response matches our brand voice:
    - Professional but friendly
    - Uses "we" not "I"
    - Avoids jargon

    Input: {input}
    Output: {output}

    Does this match our brand voice? Answer YES or NO.
    """

    def parse_response(self, llm_response: str) -> float:
        return 1.0 if "YES" in llm_response.upper() else 0.0`}</code></pre>

      <h3>Config Integration</h3>

      <pre><code>{`# eval_config.yaml
eval_suite: basic_chat

custom_evaluators:
  - module: my_app.evaluators
    class: DomainAccuracyEvaluator
  - module: my_app.evaluators
    class: BrandVoiceEvaluator

thresholds:
  domain_accuracy:
    min_mean: 0.9
  brand_voice:
    min_mean: 0.8`}</code></pre>

      <h2>Current Workaround</h2>

      <p>
        Until custom evaluators are supported, you can:
      </p>

      <ol>
        <li>Fork the repository</li>
        <li>Add your evaluator to <code>evaluators.py</code></li>
        <li>Add it to the appropriate eval suite</li>
        <li>Install from your fork</li>
      </ol>

      <pre><code>{`# In evaluators.py, add to EVAL_SUITES
EVAL_SUITES = {
    "basic_chat": [
        UserFrustrationEvaluator(),
        HelpfulnessQualityEvaluator(),
        ToxicityEvaluator(),
        MyCustomEvaluator(),  # Add here
    ],
    # ...
}`}</code></pre>

      <h2>Evaluator Interface</h2>

      <p>All evaluators must implement:</p>

      <pre><code>{`class Evaluator:
    name: str  # Unique identifier for the metric

    def evaluate(
        self,
        input: str,
        output: str,
        context: str = None,
        **kwargs
    ) -> float:
        """
        Returns a score between 0.0 and 1.0.
        - 1.0 = pass
        - 0.0 = fail
        """
        raise NotImplementedError`}</code></pre>
    </div>
  )
}
