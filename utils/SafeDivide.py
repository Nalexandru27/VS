import pandas as pd

# def safe_divide(numerator, denominator):
#     if numerator is None or denominator is None or denominator == 0:
#         return 0  # Evită eroarea prin returnarea unei valori sigure
#     return numerator / denominator

def safe_divide(numerator, denominator):
    # Dacă sunt None, returnează 0
    if numerator is None or denominator is None:
        return 0
        
    # Dacă denominator este o serie pandas
    if isinstance(denominator, pd.Series) or isinstance(denominator, pd.DataFrame):
        # Copie pentru a evita avertismentul SettingWithCopyWarning
        result = pd.Series(index=denominator.index, dtype=float)
        
        # Dacă numerator este și el o serie, împărțiți element cu element
        if isinstance(numerator, pd.Series) or isinstance(numerator, pd.DataFrame):
            for idx in denominator.index:
                if denominator.loc[idx].item() == 0:  # .item() extrage valoarea scalară
                    result.loc[idx] = 0
                else:
                    result.loc[idx] = numerator.loc[idx] / denominator.loc[idx]
        else:
            # Numerator este scalar, denominator este serie
            for idx in denominator.index:
                if denominator.loc[idx].item() == 0:
                    result.loc[idx] = 0
                else:
                    result.loc[idx] = numerator / denominator.loc[idx]
        
        return result
    
    # Ambele sunt scalare
    if denominator == 0:
        return 0
        
    return numerator / denominator