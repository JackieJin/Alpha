
import numpy as np
import pandas as pd
import pandas.computation.expressions as expressions


def fillnan(x, y, needs_i8_conversion=False):
    x_values = x.values if hasattr(x, 'values') else x
    y_values = y.values if hasattr(y, 'values') else y
    if needs_i8_conversion:
        mask = pd.notnull(y)
        x_values = x_values.view('i8')
        y_values = y_values.view('i8')
    else:
        mask = pd.notnull(y_values)

    return expressions.where(mask, y_values, x_values, raise_on_error=True)



if __name__ == '__main__':
    c = fillnan(np.array([float('nan'), 10]), np.array([1, float('nan')]))
    t2 = pd.DataFrame({'a': np.random.randn(6), 'c': np.random.randn(6)})
    t1 = pd.DataFrame({'a': np.random.randn(3), 'b': np.random.randn(3)})
    t3 = t1.combine(t2, lambda a, b: fillnan(a,b))
    print(t1)
    print(t2)
    print(t3)