import plotly.graph_objects as go

# === Palette DPE Officielle adaptée aux classes agrégées ===
DPE_COLORS = {
    'A_B': '#009966',   # Vert foncé 
    'C':   '#CCFF33',   # Jaune-vert
    'D':   '#FFCC00',   # Jaune
    'E':   '#FF6600',   # Orange
    'F_G': '#FF0000'    # Rouge
}

# === Fonctions ===

def display_dpe_badge(etiquette: str) -> str:
    """
    Génère un badge coloré pour l'étiquette DPE (groupée)
    """
    color = DPE_COLORS.get(etiquette, '#999999')
    return f"""
    <div class="dpe-badge" style="
        background-color: {color};
        color: white;
        padding: 8px 16px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        margin: 8px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        ">
        Étiquette énergétique : {etiquette}
    </div>
    """

def create_dpe_gauge(etiquette: str):
    """
    Crée une jauge Plotly adaptée aux classes DPE regroupées (A_B, C, D, E, F_G)
    """
    categories = list(DPE_COLORS.keys())
    colors = list(DPE_COLORS.values())

    if etiquette not in categories:
        etiquette = 'D'  # valeur par défaut si inconnue

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=categories.index(etiquette) + 1,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"DPE : {etiquette}",
            'font': {'size': 24, 'color': DPE_COLORS[etiquette]}
        },
        gauge={
            'axis': {
                'range': [1, len(categories)],
                'tickvals': list(range(1, len(categories) + 1)),
                'ticktext': categories,
                'tickfont': {'size': 14}
            },
            'bar': {'color': DPE_COLORS[etiquette]},
            'steps': [
                {'range': [i + 1, i + 2], 'color': colors[i]} for i in range(len(colors))
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': categories.index(etiquette) + 1
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333", size=14)
    )

    return fig

def get_dpe_color(etiquette: str) -> str:
    """
    Retourne la couleur officielle associée à une étiquette groupée
    """
    return DPE_COLORS.get(etiquette, '#999999')
