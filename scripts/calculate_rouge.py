from rouge_score import rouge_scorer

def calculate_rouge(summary, content):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    if not summary or not content:
        return 0.0, 0.0, 0.0
    scores = scorer.score(content, summary)
    return scores['rouge1'].fmeasure, scores['rouge2'].fmeasure, scores['rougeL'].fmeasure
