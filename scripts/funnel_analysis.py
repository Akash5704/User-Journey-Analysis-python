import pandas as pd
import re

# -------------------------------
# Funnel Analysis Core Functions
# -------------------------------

def load_data(file_path):
    """
    Loads the user journey CSV and performs basic cleaning.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found. Please ensure it exists.")
        return None

    df['user_journey'] = df['user_journey'].astype(str).fillna('')
    df['journey_length'] = df['user_journey'].apply(lambda x: len(x.split('-')) if x else 0)
    return df


def run_funnel_analysis(data, steps):
    """
    Performs sequential funnel analysis and returns a DataFrame with conversion rates.
    """
    funnel_counts = pd.Series(index=steps, dtype=int)
    retained_sessions = data.copy()

    for i, step in enumerate(steps):
        if i == 0:
            retained_sessions = retained_sessions[retained_sessions['user_journey'].str.contains(step, na=False)]
            funnel_counts[step] = len(retained_sessions)
        else:
            prev_step = steps[i - 1]
            pattern = f'{prev_step}.*-{step}'
            retained_sessions = retained_sessions[retained_sessions['user_journey'].str.contains(pattern, na=False)]
            funnel_counts[step] = len(retained_sessions)

    funnel_data = pd.DataFrame(funnel_counts, columns=['Sessions'])
    funnel_data['Step Conversion Rate'] = (funnel_data['Sessions'] / funnel_data['Sessions'].shift(1)) * 100
    funnel_data['Step Conversion Rate'] = funnel_data['Step Conversion Rate'].fillna(100).round(2)
    return funnel_data


def get_top_starting_pages(df, top_n=5):
    """
    Returns the top N most frequent starting pages.
    """
    df['first_step'] = df['user_journey'].apply(lambda x: x.split('-')[0] if x else 'Missing')
    return df['first_step'].value_counts().head(top_n)


def get_top_step_transitions(df, top_n=10):
    """
    Returns the top N most common consecutive step transitions.
    """
    path_segments = []
    for path in df['user_journey'].str.split('-'):
        if len(path) > 1:
            for i in range(len(path) - 1):
                path_segments.append(f"{path[i]} -> {path[i+1]}")

    path_counts = pd.Series(path_segments).value_counts().head(top_n)
    return path_counts


# -------------------------------
# If run directly, test basic output
# -------------------------------
if __name__ == "__main__":
    FUNNEL_STEPS = ['Homepage', 'Career tracks', 'Pricing', 'Sign up', 'Checkout']

    df = load_data("../Data/user_journey_raw.csv")
    if df is not None:
        funnel_results = run_funnel_analysis(df, FUNNEL_STEPS)
        print("\n--- Sequential Funnel Analysis Results ---")
        print(funnel_results)

        print("\n--- Top Starting Pages ---")
        print(get_top_starting_pages(df))

        print("\n--- Top Step Transitions ---")
        print(get_top_step_transitions(df))
