import re

def extract_suggestion(text):
    # text = """
    # Next, you can:
    # [1] Perform hyperparameter tuning of the random forest model to improve classification performance.
    # [2] Try other classification algorithms such as SVM or neural networks to compare results.
    # [3] Conduct feature importance analysis or dimensionality reduction to better understand the data.
    # """

    return re.findall(r'\[\d+\]\s*(.*)', text)
