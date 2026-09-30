import plotly.graph_objects as go


def histogram(series, title, xlabel):
    """Гистограмма одной переменной."""
    fig = go.Figure(go.Histogram(x=series, nbinsx=10))
    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title="Количество участников",
        bargap=0.05,
        margin=dict(l=10, r=10, t=50, b=10),
        height=320,
    )
    return fig


def scatter_with_line(x, y, slope, intercept, xlabel, ylabel, r):
    """Диаграмма рассеяния с линией регрессии."""
    x_min, x_max = float(x.min()), float(x.max())
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            name="Участники",
            marker=dict(size=9, opacity=0.6),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[x_min, x_max],
            y=[intercept + slope * x_min, intercept + slope * x_max],
            mode="lines",
            name=f"Y = {intercept:.3f} + {slope:.3f}·X",
        )
    )
    fig.update_layout(
        title=f"Диаграмма рассеяния (r = {r:.3f})",
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
        legend=dict(orientation="h", y=-0.2),
    )
    return fig