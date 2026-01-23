#!/usr/bin/env python3
"""
CO2e Impact Calculator - Estimates lives saved from carbon emission reductions

Scientific Basis for Mortality Calculations:
============================================
Primary Source: Bressler, R.D. (2021). "The mortality cost of carbon."
Nature Communications, 12, 4467. https://doi.org/10.1038/s41467-021-24487-w

Key Finding: The Mortality Cost of Carbon (MCC) is 2.26 × 10⁻⁴ excess deaths
per metric ton of CO2 emissions (range: -1.71 × 10⁻⁴ to 6.78 × 10⁻⁴).

Scientific Sources for Lifestyle CO2e Savings:
==============================================
Flight Emissions:
- myclimate Flight Calculator: https://co2.myclimate.org/
- Carbon Independent: https://www.carbonindependent.org/22.html
- Sydney-London round-trip: ~4,500 kg CO2e (includes radiative forcing)

Diet Changes:
- Scarborough et al. (2014). "Dietary greenhouse gas emissions of meat-eaters,
  fish-eaters, vegetarians and vegans in the UK." Climatic Change.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4372775/
- Our World in Data: https://ourworldindata.org/food-choice-vs-eating-local
- Energy Saving Trust UK: https://energysavingtrust.org.uk/

Transportation:
- Wynes & Nicholas (2017). "The climate mitigation gap." Environmental Research Letters.
- World Resources Institute: https://www.wri.org/insights/climate-impact-behavior-shifts

Home Energy:
- Carbon Brief: https://interactive.carbonbrief.org/
- US EPA Household Carbon Footprint Calculator
"""

import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
import webbrowser


# =============================================================================
# SCIENTIFIC CONSTANTS
# =============================================================================

# Mortality Cost of Carbon (MCC) from Bressler (2021), Nature Communications
MCC_CENTRAL = Decimal("0.000226")  # deaths per metric ton CO2e
MCC_LOW = Decimal("-0.000171")     # lower bound
MCC_HIGH = Decimal("0.000678")     # upper bound

KG_PER_METRIC_TON = Decimal("1000")
PROJECTION_YEARS = 10  # User's commitment period


# =============================================================================
# LIFESTYLE CHANGES DATA
# =============================================================================

# Each entry: (id, name, annual_co2e_kg, description, source_note)
# All values represent ANNUAL savings in kg CO2e
# Sources cited in module docstring above

LIFESTYLE_CHANGES = [
    {
        "id": "flight_syd_lon",
        "name": "Avoid one Sydney-London round-trip flight per year",
        "annual_kg": 4500,
        "description": "Long-haul flights are among the most carbon-intensive activities. "
                       "A round-trip economy flight Sydney-London produces ~4,500 kg CO2e "
                       "(including radiative forcing effects at altitude).",
        "source": "myclimate, Carbon Independent"
    },
    {
        "id": "reduce_meat",
        "name": "Reduce meat consumption to 2 meals per week",
        "annual_kg": 920,
        "description": "Reducing from a typical Western diet (~7-10 meat meals/week) to just "
                       "2 meals per week saves significant emissions from livestock farming, "
                       "feed production, and land use.",
        "source": "Scarborough et al. (2014), Energy Saving Trust UK"
    },
    {
        "id": "eliminate_dairy",
        "name": "Eliminate dairy consumption",
        "annual_kg": 420,
        "description": "Dairy production generates methane from cattle and requires significant "
                       "land and water. Switching to plant-based alternatives reduces emissions.",
        "source": "Our World in Data, Poore & Nemecek (2018)"
    },
    {
        "id": "go_car_free",
        "name": "Go car-free (give up personal vehicle)",
        "annual_kg": 2400,
        "description": "Eliminating car ownership and switching to public transit, cycling, "
                       "or walking. Based on average car usage of ~12,000 km/year.",
        "source": "Wynes & Nicholas (2017), WRI"
    },
    {
        "id": "switch_ev",
        "name": "Switch from petrol/diesel car to electric vehicle",
        "annual_kg": 2000,
        "description": "EVs produce zero direct emissions and lower lifecycle emissions, "
                       "especially when charged with renewable energy. Savings depend on "
                       "local electricity grid mix.",
        "source": "IEA, EPA"
    },
    {
        "id": "renewable_energy",
        "name": "Switch home to 100% renewable energy",
        "annual_kg": 1500,
        "description": "Switching electricity provider to certified renewable sources or "
                       "installing solar panels eliminates emissions from fossil fuel "
                       "electricity generation.",
        "source": "Carbon Brief, EPA"
    },
    {
        "id": "cycle_commute",
        "name": "Cycle instead of drive for daily commute",
        "annual_kg": 500,
        "description": "Replacing one car trip per day (~10 km average) with cycling. "
                       "Also provides health benefits and reduces traffic congestion.",
        "source": "European Cyclists' Federation, ITF"
    },
    {
        "id": "short_flight",
        "name": "Avoid one short-haul flight per year (take train instead)",
        "annual_kg": 500,
        "description": "Short flights (1-3 hours) have disproportionately high emissions "
                       "due to takeoff/landing. Trains produce 5-10x fewer emissions.",
        "source": "EEA, Eurostar"
    },
    {
        "id": "reduce_food_waste",
        "name": "Reduce food waste by 50%",
        "annual_kg": 300,
        "description": "The average household wastes ~30% of food purchased. Reducing waste "
                       "saves emissions from production, transport, and landfill methane.",
        "source": "Project Drawdown, WRAP UK"
    },
    {
        "id": "energy_efficiency",
        "name": "Adopt energy-efficient home practices",
        "annual_kg": 300,
        "description": "LED lighting, efficient appliances, smart thermostats, reducing "
                       "standby power, and better insulation. Can cut home energy use by 30%.",
        "source": "Energy Saving Trust, DOE"
    },
]


# =============================================================================
# CALCULATION FUNCTIONS
# =============================================================================

def calculate_lives_saved(co2e_kg: Decimal) -> dict:
    """Calculate estimated lives saved from CO2e reduction."""
    co2e_tons = co2e_kg / KG_PER_METRIC_TON
    return {
        "central": co2e_tons * MCC_CENTRAL,
        "low": co2e_tons * MCC_LOW,
        "high": co2e_tons * MCC_HIGH,
        "co2e_tons": co2e_tons
    }


# =============================================================================
# GUI APPLICATION
# =============================================================================

class CO2eImpactCalculator:
    """Desktop application for calculating CO2e impact on mortality."""

    def __init__(self, root):
        self.root = root
        self.root.title("CO2e Impact Calculator - Lives Saved Estimator")
        self.root.geometry("800x900")
        self.root.minsize(700, 800)

        # Track selected changes
        self.change_vars = {}

        # Configure styles
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 12))
        self.style.configure("Section.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("Result.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("BigResult.TLabel", font=("Helvetica", 24, "bold"))
        self.style.configure("Info.TLabel", font=("Helvetica", 10))
        self.style.configure("Small.TLabel", font=("Helvetica", 9))

        self._create_widgets()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Lifestyle Changes Selection
        self.selection_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.selection_frame, text="Step 1: Choose Life Changes")

        # Tab 2: Results
        self.results_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.results_tab, text="Step 2: View Impact")

        # Tab 3: Methodology
        self.method_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.method_tab, text="Methodology & Sources")

        self._create_selection_tab()
        self._create_results_tab()
        self._create_methodology_tab()

    def _create_selection_tab(self):
        """Create the lifestyle changes selection interface."""
        # Header
        header = ttk.Label(
            self.selection_frame,
            text="Select Climate-Friendly Life Changes",
            style="Title.TLabel"
        )
        header.pack(pady=(0, 5))

        subtitle = ttk.Label(
            self.selection_frame,
            text="Choose the changes you commit to making. We'll calculate your 10-year impact.",
            style="Subtitle.TLabel"
        )
        subtitle.pack(pady=(0, 15))

        # Scrollable frame for checkboxes
        canvas_frame = ttk.Frame(self.selection_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create checkbox for each lifestyle change
        for i, change in enumerate(LIFESTYLE_CHANGES):
            self._create_change_card(change, i)

        # Summary and calculate button at bottom
        bottom_frame = ttk.Frame(self.selection_frame)
        bottom_frame.pack(fill=tk.X, pady=(15, 0))

        self.summary_label = ttk.Label(
            bottom_frame,
            text="Selected: 0 changes | Annual savings: 0 kg CO2e | 10-year total: 0 kg CO2e",
            style="Info.TLabel"
        )
        self.summary_label.pack(side=tk.LEFT)

        calc_btn = ttk.Button(
            bottom_frame,
            text="Calculate Lives Saved →",
            command=self._calculate_and_show_results
        )
        calc_btn.pack(side=tk.RIGHT)

    def _create_change_card(self, change: dict, index: int):
        """Create a card for a single lifestyle change option."""
        # Card frame
        card = ttk.Frame(self.scrollable_frame, relief="groove", padding="10")
        card.pack(fill=tk.X, pady=5, padx=5)

        # Checkbox variable
        var = tk.BooleanVar(value=False)
        self.change_vars[change["id"]] = var

        # Top row: checkbox + name + annual savings
        top_row = ttk.Frame(card)
        top_row.pack(fill=tk.X)

        cb = ttk.Checkbutton(
            top_row,
            variable=var,
            command=self._update_summary
        )
        cb.pack(side=tk.LEFT)

        name_label = ttk.Label(
            top_row,
            text=change["name"],
            font=("Helvetica", 11, "bold"),
            cursor="hand2"
        )
        name_label.pack(side=tk.LEFT, padx=(5, 10))
        name_label.bind("<Button-1>", lambda e, v=var: v.set(not v.get()) or self._update_summary())

        savings_label = ttk.Label(
            top_row,
            text=f"{change['annual_kg']:,} kg CO2e/year",
            foreground="green",
            font=("Helvetica", 10, "bold")
        )
        savings_label.pack(side=tk.RIGHT)

        # Description
        desc_label = ttk.Label(
            card,
            text=change["description"],
            wraplength=680,
            justify=tk.LEFT,
            style="Small.TLabel",
            foreground="gray"
        )
        desc_label.pack(fill=tk.X, padx=(25, 0), pady=(5, 0))

        # Source
        source_label = ttk.Label(
            card,
            text=f"Source: {change['source']}",
            style="Small.TLabel",
            foreground="blue"
        )
        source_label.pack(anchor=tk.W, padx=(25, 0))

    def _update_summary(self):
        """Update the summary label with current selections."""
        selected = []
        total_annual = 0

        for change in LIFESTYLE_CHANGES:
            if self.change_vars[change["id"]].get():
                selected.append(change)
                total_annual += change["annual_kg"]

        total_10y = total_annual * PROJECTION_YEARS

        self.summary_label.config(
            text=f"Selected: {len(selected)} changes | "
                 f"Annual savings: {total_annual:,} kg CO2e | "
                 f"10-year total: {total_10y:,} kg CO2e"
        )

    def _create_results_tab(self):
        """Create the results display interface."""
        # This will be populated when calculate is clicked
        self.results_content = ttk.Frame(self.results_tab)
        self.results_content.pack(fill=tk.BOTH, expand=True)

        placeholder = ttk.Label(
            self.results_content,
            text="Select lifestyle changes in Step 1, then click 'Calculate Lives Saved'",
            style="Subtitle.TLabel"
        )
        placeholder.pack(expand=True)

    def _calculate_and_show_results(self):
        """Calculate impact and display results."""
        # Gather selected changes
        selected = []
        for change in LIFESTYLE_CHANGES:
            if self.change_vars[change["id"]].get():
                selected.append(change)

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select at least one lifestyle change to calculate impact."
            )
            return

        # Calculate totals
        total_annual = sum(c["annual_kg"] for c in selected)
        total_10y = total_annual * PROJECTION_YEARS

        # Calculate lives saved
        results = calculate_lives_saved(Decimal(total_10y))

        # Clear and rebuild results tab
        for widget in self.results_content.winfo_children():
            widget.destroy()

        # Create scrollable results
        canvas = tk.Canvas(self.results_content, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.results_content, orient="vertical", command=canvas.yview)
        results_frame = ttk.Frame(canvas)

        results_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=results_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Header
        header = ttk.Label(
            results_frame,
            text="Your Climate Impact Over 10 Years",
            style="Title.TLabel"
        )
        header.pack(pady=(0, 20))

        # Big number: Lives saved
        central = float(results["central"])
        lives_frame = ttk.Frame(results_frame)
        lives_frame.pack(pady=10)

        ttk.Label(
            lives_frame,
            text="Estimated Lives Saved:",
            style="Section.TLabel"
        ).pack()

        if central >= 0.01:
            lives_text = f"{central:.4f}"
        else:
            lives_text = f"{central:.6f}"

        lives_label = ttk.Label(
            lives_frame,
            text=lives_text,
            style="BigResult.TLabel",
            foreground="green"
        )
        lives_label.pack()

        # Uncertainty range
        low = float(results["low"])
        high = float(results["high"])
        range_text = f"(Range: {low:.6f} to {high:.6f})"
        ttk.Label(lives_frame, text=range_text, style="Small.TLabel").pack()

        # CO2e summary
        ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15, padx=20)

        co2_frame = ttk.LabelFrame(results_frame, text="CO2e Savings Breakdown", padding="15")
        co2_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(
            co2_frame,
            text=f"Annual CO2e savings: {total_annual:,} kg ({total_annual/1000:.2f} metric tons)",
            style="Info.TLabel"
        ).pack(anchor=tk.W)

        ttk.Label(
            co2_frame,
            text=f"10-Year CO2e savings: {total_10y:,} kg ({total_10y/1000:.2f} metric tons)",
            font=("Helvetica", 11, "bold")
        ).pack(anchor=tk.W, pady=(5, 0))

        # Selected changes breakdown
        changes_frame = ttk.LabelFrame(results_frame, text="Your Committed Changes", padding="15")
        changes_frame.pack(fill=tk.X, padx=20, pady=10)

        for change in selected:
            row = ttk.Frame(changes_frame)
            row.pack(fill=tk.X, pady=2)

            ttk.Label(row, text="✓", foreground="green").pack(side=tk.LEFT)
            ttk.Label(row, text=change["name"], style="Info.TLabel").pack(side=tk.LEFT, padx=(5, 10))
            ttk.Label(
                row,
                text=f"{change['annual_kg']:,} kg/year × 10 = {change['annual_kg'] * 10:,} kg",
                foreground="gray"
            ).pack(side=tk.RIGHT)

        # Interpretation
        interp_frame = ttk.LabelFrame(results_frame, text="What This Means", padding="15")
        interp_frame.pack(fill=tk.X, padx=20, pady=10)

        if central >= 1:
            interpretation = (
                f"Your commitment could prevent approximately {central:.1f} premature deaths "
                f"from temperature-related causes over the next ~80 years."
            )
        elif central >= 0.1:
            interpretation = (
                f"Your commitment represents about {central*100:.1f}% of preventing one "
                f"premature death from climate-related temperature stress."
            )
        elif central >= 0.01:
            interpretation = (
                f"Your commitment represents about {central*100:.2f}% of preventing one "
                f"premature death. Every contribution matters!"
            )
        else:
            people_needed = int(1 / central) if central > 0 else 0
            interpretation = (
                f"If {people_needed:,} people made these same commitments, together you would "
                f"prevent approximately 1 premature death from climate change."
            )

        ttk.Label(
            interp_frame,
            text=interpretation,
            wraplength=650,
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        # Caveat
        caveat_text = (
            "Note: This estimate only includes direct temperature-related mortality (heat/cold stress). "
            "It does NOT include deaths from storms, floods, crop failures, infectious diseases, "
            "or conflict. The actual total lives saved is likely HIGHER than shown."
        )
        ttk.Label(
            interp_frame,
            text=caveat_text,
            wraplength=650,
            justify=tk.LEFT,
            foreground="gray",
            font=("Helvetica", 9, "italic")
        ).pack(anchor=tk.W, pady=(10, 0))

        # Switch to results tab
        self.notebook.select(1)

    def _create_methodology_tab(self):
        """Create the methodology and sources tab."""
        # Scrollable
        canvas = tk.Canvas(self.method_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.method_tab, orient="vertical", command=canvas.yview)
        method_frame = ttk.Frame(canvas)

        method_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=method_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Title
        ttk.Label(
            method_frame,
            text="Methodology & Scientific Sources",
            style="Title.TLabel"
        ).pack(pady=(0, 15), anchor=tk.W)

        # Mortality calculation
        mort_frame = ttk.LabelFrame(method_frame, text="Lives Saved Calculation", padding="15")
        mort_frame.pack(fill=tk.X, pady=10)

        mort_text = """Formula:
Lives Saved = (Total CO2e in kg ÷ 1000) × 0.000226

This uses the "Mortality Cost of Carbon" (MCC) metric:
• Central estimate: 2.26 × 10⁻⁴ deaths per metric ton CO2e
• Equals approximately 1 life per 4,434 metric tons of CO2e
• Timeframe: Deaths prevented over 2020-2100 (~80 years)

The MCC was derived by:
1. Extending the DICE-2016 integrated assessment model
2. Adding temperature-mortality damage functions from epidemiological studies
3. Using meta-analysis of global temperature-mortality relationships
4. Projecting deaths under baseline emissions scenarios"""

        ttk.Label(
            mort_frame,
            text=mort_text,
            justify=tk.LEFT,
            wraplength=650
        ).pack(anchor=tk.W)

        # Link to paper
        link_frame = ttk.Frame(mort_frame)
        link_frame.pack(anchor=tk.W, pady=(10, 0))

        ttk.Label(link_frame, text="Primary Source: ").pack(side=tk.LEFT)
        link = ttk.Label(
            link_frame,
            text="Bressler (2021) - Nature Communications",
            foreground="blue",
            cursor="hand2",
            font=("Helvetica", 10, "underline")
        )
        link.pack(side=tk.LEFT)
        link.bind("<Button-1>", lambda e: webbrowser.open(
            "https://www.nature.com/articles/s41467-021-24487-w"
        ))

        # CO2e sources
        co2_frame = ttk.LabelFrame(method_frame, text="CO2e Savings Sources", padding="15")
        co2_frame.pack(fill=tk.X, pady=10)

        sources_text = """Lifestyle Change CO2e Values:

• Flight emissions: myclimate calculator, Carbon Independent
  (includes radiative forcing multiplier for high-altitude emissions)

• Diet changes: Scarborough et al. (2014) "Dietary greenhouse gas emissions"
  published in Climatic Change; Our World in Data; Energy Saving Trust UK

• Transportation: Wynes & Nicholas (2017) "The climate mitigation gap"
  Environmental Research Letters; World Resources Institute

• Home energy: Carbon Brief, US EPA, Energy Saving Trust

• Food waste: Project Drawdown, WRAP UK

All values represent conservative estimates based on peer-reviewed research
and government environmental agency data."""

        ttk.Label(
            co2_frame,
            text=sources_text,
            justify=tk.LEFT,
            wraplength=650
        ).pack(anchor=tk.W)

        # Important limitations
        limit_frame = ttk.LabelFrame(method_frame, text="Important Limitations", padding="15")
        limit_frame.pack(fill=tk.X, pady=10)

        limit_text = """• The MCC only includes direct temperature-related mortality (heat/cold stress)

• Does NOT include deaths from: storms, floods, droughts, crop failures,
  infectious disease spread, water scarcity, conflict, or migration

• Actual total climate mortality impact is likely HIGHER than calculated

• CO2e savings estimates vary by region, lifestyle, and individual circumstances

• Estimates have significant uncertainty ranges (shown in results)

• Based on 2020 baseline emissions scenario projections"""

        ttk.Label(
            limit_frame,
            text=limit_text,
            justify=tk.LEFT,
            wraplength=650
        ).pack(anchor=tk.W)


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = CO2eImpactCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
