import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx

# ============================================================================
# CONFIGURATION
# ============================================================================
STUDENT_NAME = "AGOUSSAL CHAIMAA"
PROFESSOR_NAME = "Dr. EL MKHALET MOUNA"
SCHOOL = "Mohammadia School of Engineers (EMI)"

# Color scheme - Rose Pink and Navy Blue
C_BG = "#f5e6f0"  # Light rose pink background
C_BLUE = "#001f3f"  # Navy blue
C_RED = "#d91e63"  # Rose pink/magenta
C_HELP_BG = "#ffe6f0"  # Very light rose pink for help boxes
C_NAVY = "#001f3f"  # Navy blue
C_ROSE = "#d91e63"  # Rose pink
C_LIGHT_ROSE = "#f8bbd0"  # Light rose for accents

# ============================================================================
# LOGIQUE DU SIMPLEXE
# ============================================================================
class SimplexSolver:
    """Solveur simplexe pour la forme standard : Max Z = CX avec AX <= B"""
    @staticmethod
    def solve(c, A, b):
        num_vars = len(c)
        num_constraints = len(A)
        
        tableau = np.zeros((num_constraints + 1, num_vars + num_constraints + 1))
        tableau[:num_constraints, :num_vars] = A
        tableau[:num_constraints, num_vars:num_vars + num_constraints] = np.eye(num_constraints)
        tableau[:num_constraints, -1] = b
        tableau[-1, :num_vars] = -np.array(c)
        
        history = []
        history.append(tableau.copy())

        iteration = 0
        while np.min(tableau[-1, :-1]) < -1e-10 and iteration < 50:
            pivot_col = np.argmin(tableau[-1, :-1])
            
            ratios = []
            for i in range(num_constraints):
                if tableau[i, pivot_col] > 1e-10:
                    ratios.append(tableau[i, -1] / tableau[i, pivot_col])
                else:
                    ratios.append(np.inf)
            
            if np.all(np.array(ratios) == np.inf):
                return None, "Solution non bornée"
            
            pivot_row = np.argmin(ratios)
            
            pivot_element = tableau[pivot_row, pivot_col]
            if abs(pivot_element) < 1e-10:
                break
            tableau[pivot_row] /= pivot_element
            
            for i in range(num_constraints + 1):
                if i != pivot_row and abs(tableau[i, pivot_col]) > 1e-10:
                    tableau[i] -= tableau[i, pivot_col] * tableau[pivot_row]
            
            history.append(tableau.copy())
            iteration += 1

        return tableau, history

# ============================================================================
# TRANSPORTATION PROBLEM SOLVER
# ============================================================================
class TransportationSolver:
    """Solveur pour le problème de transport (Vogel's Approximation Method)"""
    @staticmethod
    def solve(supply, demand, costs):
        """
        supply: array of supply at each source
        demand: array of demand at each destination
        costs: 2D array of unit costs
        """
        supply = np.array(supply, dtype=float)
        demand = np.array(demand, dtype=float)
        costs = np.array(costs, dtype=float)
        
        m, n = costs.shape
        allocation = np.zeros((m, n))
        
        supply_copy = supply.copy()
        demand_copy = demand.copy()
        
        result = {"allocations": [], "total_cost": 0}
        
        while np.sum(supply_copy) > 1e-10 and np.sum(demand_copy) > 1e-10:
            # Calculate penalties
            row_penalties = []
            col_penalties = []
            
            for i in range(m):
                if supply_copy[i] > 1e-10:
                    sorted_costs = np.sort(costs[i, :][demand_copy > 1e-10])
                    if len(sorted_costs) >= 2:
                        row_penalties.append((sorted_costs[1] - sorted_costs[0], i, 'row'))
                    elif len(sorted_costs) == 1:
                        row_penalties.append((sorted_costs[0], i, 'row'))
            
            for j in range(n):
                if demand_copy[j] > 1e-10:
                    sorted_costs = np.sort(costs[:, j][supply_copy > 1e-10])
                    if len(sorted_costs) >= 2:
                        col_penalties.append((sorted_costs[1] - sorted_costs[0], j, 'col'))
                    elif len(sorted_costs) == 1:
                        col_penalties.append((sorted_costs[0], j, 'col'))
            
            if not row_penalties and not col_penalties:
                break
            
            penalties = row_penalties + col_penalties
            penalties.sort(reverse=True)
            
            if penalties:
                _, idx, ptype = penalties[0]
                
                if ptype == 'row':
                    i = idx
                    j = np.argmin(costs[i, :])
                else:
                    j = idx
                    i = np.argmin(costs[:, j])
                
                transfer = min(supply_copy[i], demand_copy[j])
                allocation[i, j] += transfer
                supply_copy[i] -= transfer
                demand_copy[j] -= transfer
                result["allocations"].append((i, j, transfer, costs[i, j]))
                result["total_cost"] += transfer * costs[i, j]
        
        result["allocation_matrix"] = allocation
        return result

# ============================================================================
# UTILITY FUNCTIONS FOR UI
# ============================================================================
def make_card(root, pad=10):
    """Create a card frame with border"""
    outer = tk.Frame(root, bg=C_BG, bd=3, relief='solid',
                     highlightbackground=C_NAVY, highlightthickness=3)
    inner = tk.Frame(outer, bg=C_BG)
    inner.pack(padx=pad, pady=pad, fill='both', expand=True)
    return outer, inner

def primary_btn(parent, text, cmd):
    """Create primary button"""
    return tk.Button(parent, text=text, command=cmd, font=("Arial", 11, "bold"),
                    bg='white', fg=C_NAVY, width=25, height=2, bd=2, relief='solid', cursor='hand2')

def success_btn(parent, text, cmd):
    """Create success button"""
    return tk.Button(parent, text=text, command=cmd, font=("Arial", 11, "bold"),
                    bg=C_ROSE, fg='white', width=25, height=2, bd=2, relief='solid', cursor='hand2')

def back_btn(parent, cmd):
    """Create back button"""
    return tk.Button(parent, text="< Back to Menu", command=cmd,
                    font=("Arial", 11), bg='white', fg=C_NAVY,
                    width=18, bd=2, relief='solid', cursor='hand2')

class TextWindow:
    """Display text in a new window"""
    def __init__(self, parent, title, text):
        win = tk.Toplevel(parent)
        win.title(title)
        win.geometry("900x600")
        win.configure(bg=C_BG)
        
        # Header
        header = tk.Frame(win, bg=C_NAVY, height=40)
        header.pack(fill='x')
        tk.Label(header, text=title, font=("Arial", 12, "bold"), bg=C_NAVY, fg=C_LIGHT_ROSE).pack(pady=8)
        
        txt = tk.Text(win, font=("Courier", 10), width=100, height=30, bg=C_BG, fg=C_NAVY)
        txt.pack(padx=10, pady=10, fill="both", expand=True)
        txt.insert("1.0", text)
        txt.config(state="disabled")

class FigureWindow:
    """Display matplotlib figure in a new window"""
    def __init__(self, parent, fig, title="Figure"):
        win = tk.Toplevel(parent)
        win.title(title)
        win.geometry("900x650")
        win.fig = fig
        win.configure(bg=C_BG)
        
        # Header
        header = tk.Frame(win, bg=C_NAVY, height=40)
        header.pack(fill='x')
        tk.Label(header, text=title, font=("Arial", 12, "bold"), bg=C_NAVY, fg=C_LIGHT_ROSE).pack(pady=8)
        
        container = ttk.Frame(win, padding=8)
        container.pack(fill="both", expand=True)
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

# ============================================================================
# APPLICATION PRINCIPALE
# ============================================================================
class ElectricalEngineeringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PartieITI - Application Desktop")
        self.root.geometry("1200x800")
        self.root.configure(bg=C_BG)
        self.graph = None
        self.vertices = 10
        self.density = 0.3
        self.show_welcome()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _header(self, text):
        """Create header frame"""
        header_frame = tk.Frame(self.root, bg=C_NAVY, height=40)
        header_frame.pack(fill='x')
        tk.Label(header_frame, text=text, 
                font=("Arial", 14, "bold"), bg=C_NAVY, fg=C_LIGHT_ROSE).pack(pady=8)

    # ========================================================================
    # PAGE D'ACCUEIL
    # ========================================================================
    def show_welcome(self):
        self.clear()
        
        # Titre avec fond navy
        title_frame = tk.Frame(self.root, bg=C_NAVY, height=40)
        title_frame.pack(fill='x')
        tk.Label(title_frame, text="PartieITI - Application Desktop", 
                font=("Arial", 16, "bold"), bg=C_NAVY, fg=C_LIGHT_ROSE).pack(pady=8)
        
        # Sous-titre étape 1
        subtitle_frame = tk.Frame(self.root, bg=C_ROSE, height=30)
        subtitle_frame.pack(fill='x')
        tk.Label(subtitle_frame, text="Etape 1 - Realisation de L interface Graphique", 
                font=("Arial", 12, "bold"), bg=C_ROSE, fg='white').pack(pady=5)
        
        # Cadre principal avec bordure navy
        main_frame = tk.Frame(self.root, bg=C_BG, bd=3, relief='solid', 
                             highlightbackground=C_NAVY, highlightthickness=3)
        main_frame.pack(padx=30, pady=30, fill='both', expand=True)
        
        # Titre principal - UPDATED FOR ELECTRICAL ENGINEERING
        title = tk.Label(main_frame, 
                        text='"Development of a Desktop Application Integrating\nOperational Research, Simplex Algorithm,\nand Optimization Techniques\nin the Electrical Engineering Sector"',
                        font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY, 
                        wraplength=700, justify='center')
        title.pack(pady=30)
        
        # École
        school = tk.Label(main_frame, text="Mohammadia School of Engineers (EMI)", 
                         font=("Arial", 11, "italic"), bg=C_BG, fg=C_NAVY)
        school.pack(pady=10)
        
        # Cadre para nomes
        info_frame = tk.Frame(main_frame, bg=C_BG)
        info_frame.pack(pady=40, padx=50)
        
        # Cadre étudiant com bordure
        student_box = tk.Frame(info_frame, bg=C_LIGHT_ROSE, bd=2, relief='solid', 
                              highlightbackground=C_NAVY, highlightthickness=2)
        student_box.grid(row=0, column=0, padx=40, pady=10, sticky='ew', ipadx=20, ipady=15)
        tk.Label(student_box, text="Name of Student", font=("Arial", 10, "bold"), 
                bg=C_LIGHT_ROSE, fg=C_NAVY).pack()
        tk.Label(student_box, text=STUDENT_NAME, font=("Arial", 11), 
                bg=C_LIGHT_ROSE, fg='black').pack(pady=5)
        
        # Cadre professeur com bordure
        prof_box = tk.Frame(info_frame, bg=C_LIGHT_ROSE, bd=2, relief='solid',
                           highlightbackground=C_NAVY, highlightthickness=2)
        prof_box.grid(row=0, column=1, padx=40, pady=10, sticky='ew', ipadx=20, ipady=15)
        tk.Label(prof_box, text="Name of Professor", font=("Arial", 10, "bold"), 
                bg=C_LIGHT_ROSE, fg=C_NAVY).pack()
        tk.Label(prof_box, text=PROFESSOR_NAME, font=("Arial", 11), 
                bg=C_LIGHT_ROSE, fg='black').pack(pady=5)
        
        # Note
        note = tk.Label(main_frame, text="Operational Research & Optimization Techniques", 
                       font=("Arial", 10, "italic"), bg=C_BG, fg=C_ROSE)
        note.pack(pady=20)
        
        # Bouton START com bordure
        start_btn = tk.Button(main_frame, text="START", command=self.show_main_menu,
                             font=("Arial", 14, "bold"), bg=C_ROSE, fg='white',
                             width=20, height=2, cursor='hand2', bd=2, relief='solid')
        start_btn.pack(pady=30)

    # ========================================================================
    # MENU PRINCIPAL
    # ========================================================================
    def show_main_menu(self):
        self.clear()
        
        # Cadre principal com bordure
        main_frame = tk.Frame(self.root, bg=C_BG, bd=3, relief='solid',
                             highlightbackground=C_NAVY, highlightthickness=3)
        main_frame.pack(padx=50, pady=30, fill='both', expand=True)
        
        # Título
        tk.Label(main_frame, text="Operational Research Optimization Methods", 
                font=("Arial", 14, "bold"), bg=C_BG, fg=C_NAVY).pack(pady=20)
        
        # Cadre para algoritmos
        algo_frame = tk.Frame(main_frame, bg=C_BG)
        algo_frame.pack(padx=15, pady=15, fill='both', expand=True)
        
        buttons = [
            ("Simplex Method\n(Linear Programming)", self.show_simplex_module),
            ("Graph Coloring\n(Welsh-Powell)", self.show_welsh_powell_module),
            ("Shortest Path\n(Dijkstra)", self.show_dijkstra_module),
            ("Minimum Spanning Tree\n(Kruskal)", self.show_kruskal_module),
            ("All-Pairs Paths\n(Bellman-Ford)", self.show_bellman_ford_module),
            ("Maximum Flow\n(Ford-Fulkerson)", self.show_ford_fulkerson_module),
        ]
        
        # 2x3 layout
        for i, (text, cmd) in enumerate(buttons):
            row = i // 3
            col = i % 3
            btn = tk.Button(algo_frame, text=text, command=cmd,
                          font=("Arial", 10, "bold"), bg='white', fg=C_ROSE,
                          width=20, height=3, bd=2, relief='solid', cursor='hand2')
            btn.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
        
        # Back button at bottom
        back_btn(self.root, self.show_welcome).pack(pady=20)

    # ========================================================================
    # LINEAR PROGRAMMING - SIMPLEX
    # ========================================================================
    def show_simplex_module(self):
        self.clear()
        self._header("Linear Programming — Simplex Solution Engine")

        outer, inner = make_card(self.root, pad=20)
        outer.pack(padx=50, pady=15, fill="both", expand=True)

        help_frame = tk.Frame(inner, bg=C_HELP_BG, bd=1, relief="solid")
        help_frame.pack(fill="x", pady=(0, 15))
        tk.Label(help_frame, text="MULTI-VARIABLE FIELD INPUT INSTRUCTIONS:\n"
                                 "• Objective Coefficients (c): Input target weights separated by spaces. (e.g., 5 8 to maximize Z = 5X1 + 8X2)\n"
                                 "• Constraint Matrix (A): Coefficients for <= rows. Separate rows using semicolons ';'. (e.g., 2 1; 1 3)\n"
                                 "• Right-Hand Bounds (b): Maximum limit thresholds for each row constraint, space separated. (e.g., 40 50)", 
                 font=("Arial", 10, "bold"), fg=C_NAVY, bg=C_HELP_BG, justify="left", anchor="w", padx=15, pady=8).pack(fill="x")

        f_inputs = tk.Frame(inner, bg=C_BG)
        f_inputs.pack(fill="x", padx=10, pady=10)

        tk.Label(f_inputs, text="Objective Function Coefficients (c):", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=0, column=0, sticky="w", pady=8)
        self.ent_simp_c = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_simp_c.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(f_inputs, text="Constraint Technical Matrix (A):", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=1, column=0, sticky="w", pady=8)
        self.ent_simp_A = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_simp_A.grid(row=1, column=1, padx=15, pady=8)

        tk.Label(f_inputs, text="Right-Hand Side Bounds (b):", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=2, column=0, sticky="w", pady=8)
        self.ent_simp_b = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_simp_b.grid(row=2, column=1, padx=15, pady=8)

        f_btns = tk.Frame(inner, bg=C_BG)
        f_btns.pack(fill="x", padx=10, pady=20)

        primary_btn(f_btns, "Fill with Random Model Example", self._gen_simplex_random_fields).pack(side="left", padx=5)
        success_btn(f_btns, "Compute Optimal Simplex Solution", self._solve_simplex_from_inputs).pack(side="left", padx=25)

        self._gen_simplex_random_fields()
        back_btn(self.root, self.show_main_menu).pack(side="bottom", pady=20)

    def _gen_simplex_random_fields(self):
        rng = np.random.default_rng()
        c = rng.integers(4, 16, size=2).tolist()
        A_rows = [rng.integers(1, 5, size=2).tolist() for _ in range(3)]
        b = rng.integers(30, 70, size=3).tolist()

        self.ent_simp_c.delete(0, "end")
        self.ent_simp_c.insert(0, " ".join(map(str, c)))
        self.ent_simp_A.delete(0, "end")
        self.ent_simp_A.insert(0, "; ".join(" ".join(map(str, r)) for r in A_rows))
        self.ent_simp_b.delete(0, "end")
        self.ent_simp_b.insert(0, " ".join(map(str, b)))

    def _solve_simplex_from_inputs(self):
        try:
            c_raw = [float(x) for x in self.ent_simp_c.get().replace(",", " ").split() if x.strip()]
            A_raw = []
            for row in self.ent_simp_A.get().split(";"):
                items = [float(x) for x in row.replace(",", " ").split() if x.strip()]
                if items:
                    A_raw.append(items)
            b_raw = [float(x) for x in self.ent_simp_b.get().replace(",", " ").split() if x.strip()]
            
            c_arr = np.array(c_raw)
            A_arr = np.array(A_raw)
            b_arr = np.array(b_raw)
            
            if len(b_arr) != len(A_arr):
                messagebox.showerror("Dimensionality Conflict", f"The number of rows in bound vector b ({len(b_arr)}) does not match rows defined in matrix A ({len(A_arr)}).")
                return
        except Exception as e:
            messagebox.showerror("Input Syntax Error", f"Please check whitespace boundaries or comma placements.\nError details: {e}")
            return

        final_tab, history = SimplexSolver.solve(c_arr, A_arr, b_arr)
        
        if final_tab is None:
            messagebox.showerror("Optimization Error", "Problem is unbounded or infeasible")
            return
        
        report = "DETAILED SIMPLEX LINEAR PROGRAMMING OPTIMIZATION REPORT\n" + "="*60 + "\n\n"
        report += f"Mathematical Framework Model Formulation:\n"
        report += f"  Maximize Z = " + " + ".join([f"{c_arr[i]:.2f}*X{i+1}" for i in range(len(c_arr))]) + "\n\nBoundary Constraints Enforced:\n"
        for i in range(len(b_arr)):
            report += f"  Constraint {i+1} : " + " + ".join([f"{A_arr[i,j]:.2f}*X{j+1}" for j in range(A_arr.shape[1])]) + f" <= {b_arr[i]:.2f}\n"
        
        report += "\n" + "-"*50 + "\n"
        report += f"Analysis Status: Optimization Complete\n\n"
        report += "Optimal Decision Value Points Found:\n"
        
        num_vars = len(c_arr)
        num_constraints = len(A_arr)
        for idx in range(num_vars):
            report += f"  Variable X{idx+1} = {final_tab[num_constraints, idx]:.4f}\n"
        report += f"\nMaximum Attained Objective Function Z = {final_tab[-1, -1]:.4f}\n"

        TextWindow(self.root, "Simplex Problem Evaluation Summary", report)

        if len(c_arr) == 2:
            fig, ax = plt.subplots(figsize=(6, 4.5), dpi=110)
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            x1_v = np.linspace(0, max(b_arr)*1.5, 300)
            for i in range(len(b_arr)):
                if A_arr[i,1] > 0:
                    x2_v = (b_arr[i] - A_arr[i,0]*x1_v) / A_arr[i,1]
                    ax.plot(x1_v, x2_v, label=f"Constraint Line {i+1}", color=C_NAVY)
            ax.set_xlim(0, float(max(b_arr)))
            ax.set_ylim(0, float(max(b_arr)))
            
            # Plot optimal point
            optimal_x1 = final_tab[len(A_arr), len(c_arr)]
            optimal_x2 = final_tab[len(A_arr)-1, len(c_arr)] if len(A_arr) > 1 else 0
            ax.plot(optimal_x1, optimal_x2, "o", markersize=9, color=C_ROSE, label=f"Optimal Vertex Z={final_tab[-1, -1]:.2f}")
            
            ax.set_xlabel("X1", color=C_NAVY); ax.set_ylabel("X2", color=C_NAVY)
            ax.tick_params(colors=C_NAVY)
            ax.legend(); ax.grid(True, alpha=0.2)
            FigureWindow(self.root, fig, "Admissible Solutions Geometric Convex Region Bounds")

    # ========================================================================
    # WELSH-POWELL GRAPH COLORING
    # ========================================================================
    def show_welsh_powell_module(self):
        self.clear()
        self._header("Graph Coloring — Welsh-Powell Algorithm")

        outer, inner = make_card(self.root, pad=20)
        outer.pack(padx=50, pady=15, fill="both", expand=True)

        help_frame = tk.Frame(inner, bg=C_HELP_BG, bd=1, relief="solid")
        help_frame.pack(fill="x", pady=(0, 15))
        tk.Label(help_frame, text="GRAPH GENERATION PARAMETERS:\n"
                                 "• Number of Vertices: Range 1-100. Creates nodes for the graph\n"
                                 "• Graph Density: Percentage (1-100%) of edges present relative to maximum possible edges\n"
                                 "Welsh-Powell: Greedy vertex coloring algorithm",
                 font=("Arial", 10, "bold"), fg=C_NAVY, bg=C_HELP_BG, justify="left", anchor="w", padx=15, pady=8).pack(fill="x")

        f_inputs = tk.Frame(inner, bg=C_BG)
        f_inputs.pack(fill="x", padx=10, pady=10)

        tk.Label(f_inputs, text="Number of Vertices:", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=0, column=0, sticky="w", pady=8)
        self.ent_wp_vertices = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_wp_vertices.insert(0, "10")
        self.ent_wp_vertices.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(f_inputs, text="Graph Density (%):", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=1, column=0, sticky="w", pady=8)
        self.ent_wp_density = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_wp_density.insert(0, "30")
        self.ent_wp_density.grid(row=1, column=1, padx=15, pady=8)

        f_btns = tk.Frame(inner, bg=C_BG)
        f_btns.pack(fill="x", padx=10, pady=20)

        success_btn(f_btns, "Generate & Solve Welsh-Powell", self._solve_welsh_powell).pack(side="left", padx=25)

        back_btn(self.root, self.show_main_menu).pack(side="bottom", pady=20)

    def _solve_welsh_powell(self):
        try:
            vertices = int(self.ent_wp_vertices.get())
            density = float(self.ent_wp_density.get()) / 100
            
            if not (1 <= vertices <= 100) or not (0 < density <= 1):
                messagebox.showerror("Input Error", "Vertices: 1-100, Density: 1-100%")
                return
            
            graph = nx.gnp_random_graph(vertices, density, seed=42)
            coloring = nx.greedy_color(graph, strategy='largest_first')
            num_colors = max(coloring.values()) + 1
            
            report = f"WELSH-POWELL GRAPH COLORING ANALYSIS\n" + "="*60 + "\n\n"
            report += f"Graph Properties:\n"
            report += f"  Vertices: {vertices}\n"
            report += f"  Edges: {graph.number_of_edges()}\n"
            report += f"  Chromatic Number: {num_colors}\n\n"
            report += f"Node Coloring Assignment:\n"
            for node in sorted(coloring.keys())[:20]:
                report += f"  Node {node}: Color {coloring[node]}\n"
            
            TextWindow(self.root, "Welsh-Powell Results", report)
            
            fig = Figure(figsize=(12, 9), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            pos = nx.spring_layout(graph, seed=42)
            colors = [coloring[node] for node in graph.nodes()]
            nx.draw_networkx_nodes(graph, pos, node_color=colors, cmap='tab20', node_size=500, ax=ax)
            nx.draw_networkx_edges(graph, pos, alpha=0.3, ax=ax, edge_color=C_NAVY)
            nx.draw_networkx_labels(graph, pos, font_size=9, ax=ax)
            ax.set_title(f'Welsh-Powell Coloring: {num_colors} colors', fontsize=16, fontweight='bold', color=C_NAVY)
            ax.axis('off')
            FigureWindow(self.root, fig, "Welsh-Powell Graph Visualization")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ========================================================================
    # DIJKSTRA SHORTEST PATH
    # ========================================================================
    def show_dijkstra_module(self):
        self.clear()
        self._header("Shortest Path — Dijkstra Algorithm")

        outer, inner = make_card(self.root, pad=20)
        outer.pack(padx=50, pady=15, fill="both", expand=True)

        help_frame = tk.Frame(inner, bg=C_HELP_BG, bd=1, relief="solid")
        help_frame.pack(fill="x", pady=(0, 15))
        tk.Label(help_frame, text="DIJKSTRA'S ALGORITHM PARAMETERS:\n"
                                 "• Number of Vertices: Range 1-100\n"
                                 "• Graph Density: Edge percentage (1-100%)\n"
                                 "Finds the shortest path between two nodes",
                 font=("Arial", 10, "bold"), fg=C_NAVY, bg=C_HELP_BG, justify="left", anchor="w", padx=15, pady=8).pack(fill="x")

        f_inputs = tk.Frame(inner, bg=C_BG)
        f_inputs.pack(fill="x", padx=10, pady=10)

        tk.Label(f_inputs, text="Number of Vertices:", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=0, column=0, sticky="w", pady=8)
        self.ent_dij_vertices = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_dij_vertices.insert(0, "10")
        self.ent_dij_vertices.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(f_inputs, text="Graph Density (%):", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=1, column=0, sticky="w", pady=8)
        self.ent_dij_density = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_dij_density.insert(0, "30")
        self.ent_dij_density.grid(row=1, column=1, padx=15, pady=8)

        f_btns = tk.Frame(inner, bg=C_BG)
        f_btns.pack(fill="x", padx=10, pady=20)

        success_btn(f_btns, "Generate & Solve Dijkstra", self._solve_dijkstra).pack(side="left", padx=25)

        back_btn(self.root, self.show_main_menu).pack(side="bottom", pady=20)

    def _solve_dijkstra(self):
        try:
            vertices = int(self.ent_dij_vertices.get())
            density = float(self.ent_dij_density.get()) / 100
            
            if not (1 <= vertices <= 100) or not (0 < density <= 1):
                messagebox.showerror("Input Error", "Vertices: 1-100, Density: 1-100%")
                return
            
            graph = nx.gnp_random_graph(vertices, density, seed=42)
            for (u, v) in graph.edges():
                graph[u][v]['weight'] = np.random.randint(1, 20)
            
            start, end = 0, min(vertices-1, 9)
            path = nx.shortest_path(graph, start, end, weight='weight')
            length = nx.shortest_path_length(graph, start, end, weight='weight')
            
            report = f"DIJKSTRA SHORTEST PATH ANALYSIS\n" + "="*60 + "\n\n"
            report += f"Path from Node {start} to Node {end}:\n"
            report += f"  {' → '.join(map(str, path))}\n"
            report += f"  Total Distance: {length:.2f}\n\n"
            
            TextWindow(self.root, "Dijkstra Results", report)
            
            fig = Figure(figsize=(12, 9), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            pos = nx.spring_layout(graph, seed=42)
            nx.draw_networkx_nodes(graph, pos, node_color=C_LIGHT_ROSE, node_size=500, ax=ax)
            nx.draw_networkx_edges(graph, pos, alpha=0.2, ax=ax, edge_color=C_NAVY)
            path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color=C_ROSE, width=3, ax=ax)
            nx.draw_networkx_nodes(graph, pos, nodelist=[start], node_color=C_NAVY, node_size=700, ax=ax)
            nx.draw_networkx_nodes(graph, pos, nodelist=[end], node_color=C_ROSE, node_size=700, ax=ax)
            nx.draw_networkx_labels(graph, pos, font_size=10, ax=ax)
            ax.set_title(f'Dijkstra: {start} → {end} (Distance: {length:.0f})', fontsize=16, fontweight='bold', color=C_NAVY)
            ax.axis('off')
            FigureWindow(self.root, fig, "Dijkstra Shortest Path Visualization")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ========================================================================
    # KRUSKAL MINIMUM SPANNING TREE
    # ========================================================================
    def show_kruskal_module(self):
        self.clear()
        self._header("Minimum Spanning Tree — Kruskal Algorithm")

        outer, inner = make_card(self.root, pad=20)
        outer.pack(padx=50, pady=15, fill="both", expand=True)

        help_frame = tk.Frame(inner, bg=C_HELP_BG, bd=1, relief="solid")
        help_frame.pack(fill="x", pady=(0, 15))
        tk.Label(help_frame, text="KRUSKAL'S MST ALGORITHM PARAMETERS:\n"
                                 "• Number of Vertices: Range 1-100\n"
                                 "• Graph Density: Edge percentage (1-100%)\n"
                                 "Finds the minimum weight spanning tree",
                 font=("Arial", 10, "bold"), fg=C_NAVY, bg=C_HELP_BG, justify="left", anchor="w", padx=15, pady=8).pack(fill="x")

        f_inputs = tk.Frame(inner, bg=C_BG)
        f_inputs.pack(fill="x", padx=10, pady=10)

        tk.Label(f_inputs, text="Number of Vertices:", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=0, column=0, sticky="w", pady=8)
        self.ent_kru_vertices = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_kru_vertices.insert(0, "10")
        self.ent_kru_vertices.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(f_inputs, text="Graph Density (%):", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=1, column=0, sticky="w", pady=8)
        self.ent_kru_density = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_kru_density.insert(0, "30")
        self.ent_kru_density.grid(row=1, column=1, padx=15, pady=8)

        f_btns = tk.Frame(inner, bg=C_BG)
        f_btns.pack(fill="x", padx=10, pady=20)

        success_btn(f_btns, "Generate & Solve Kruskal", self._solve_kruskal).pack(side="left", padx=25)

        back_btn(self.root, self.show_main_menu).pack(side="bottom", pady=20)

    def _solve_kruskal(self):
        try:
            vertices = int(self.ent_kru_vertices.get())
            density = float(self.ent_kru_density.get()) / 100
            
            if not (1 <= vertices <= 100) or not (0 < density <= 1):
                messagebox.showerror("Input Error", "Vertices: 1-100, Density: 1-100%")
                return
            
            graph = nx.gnp_random_graph(vertices, density, seed=42)
            for (u, v) in graph.edges():
                graph[u][v]['weight'] = np.random.randint(1, 20)
            
            mst = nx.minimum_spanning_tree(graph)
            weight = sum(mst[u][v]['weight'] for u, v in mst.edges())
            
            report = f"KRUSKAL MST ANALYSIS\n" + "="*60 + "\n\n"
            report += f"Graph Properties:\n"
            report += f"  Vertices: {vertices}\n"
            report += f"  Original Edges: {graph.number_of_edges()}\n"
            report += f"  MST Edges: {mst.number_of_edges()}\n"
            report += f"  Total MST Weight: {weight:.2f}\n\n"
            
            TextWindow(self.root, "Kruskal Results", report)
            
            fig = Figure(figsize=(16, 7), dpi=100)
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            ax1.set_facecolor(C_BG)
            ax2.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            pos = nx.spring_layout(graph, seed=42)
            nx.draw_networkx(graph, pos, ax=ax1, node_color=C_LIGHT_ROSE, node_size=400, edge_color=C_NAVY)
            edge_labels = nx.get_edge_attributes(graph, 'weight')
            nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=7, ax=ax1)
            ax1.set_title('Original Graph', color=C_NAVY)
            ax1.axis('off')
            nx.draw_networkx(mst, pos, ax=ax2, node_color=C_LIGHT_ROSE, node_size=400, edge_color=C_ROSE, width=2)
            mst_labels = nx.get_edge_attributes(mst, 'weight')
            nx.draw_networkx_edge_labels(mst, pos, mst_labels, font_size=7, ax=ax2)
            ax2.set_title(f'MST - Weight: {weight}', color=C_NAVY)
            ax2.axis('off')
            FigureWindow(self.root, fig, "Kruskal MST Visualization")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ========================================================================
    # BELLMAN-FORD ALL-PAIRS PATHS
    # ========================================================================
    def show_bellman_ford_module(self):
        self.clear()
        self._header("All-Pairs Shortest Paths — Bellman-Ford Algorithm")

        outer, inner = make_card(self.root, pad=20)
        outer.pack(padx=50, pady=15, fill="both", expand=True)

        help_frame = tk.Frame(inner, bg=C_HELP_BG, bd=1, relief="solid")
        help_frame.pack(fill="x", pady=(0, 15))
        tk.Label(help_frame, text="BELLMAN-FORD ALGORITHM PARAMETERS:\n"
                                 "• Number of Vertices: Range 1-100\n"
                                 "• Graph Density: Edge percentage (1-100%)\n"
                                 "Computes shortest paths from a source to all other vertices",
                 font=("Arial", 10, "bold"), fg=C_NAVY, bg=C_HELP_BG, justify="left", anchor="w", padx=15, pady=8).pack(fill="x")

        f_inputs = tk.Frame(inner, bg=C_BG)
        f_inputs.pack(fill="x", padx=10, pady=10)

        tk.Label(f_inputs, text="Number of Vertices:", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=0, column=0, sticky="w", pady=8)
        self.ent_bf_vertices = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_bf_vertices.insert(0, "10")
        self.ent_bf_vertices.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(f_inputs, text="Graph Density (%):", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=1, column=0, sticky="w", pady=8)
        self.ent_bf_density = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_bf_density.insert(0, "30")
        self.ent_bf_density.grid(row=1, column=1, padx=15, pady=8)

        f_btns = tk.Frame(inner, bg=C_BG)
        f_btns.pack(fill="x", padx=10, pady=20)

        success_btn(f_btns, "Generate & Solve Bellman-Ford", self._solve_bellman_ford).pack(side="left", padx=25)

        back_btn(self.root, self.show_main_menu).pack(side="bottom", pady=20)

    def _solve_bellman_ford(self):
        try:
            vertices = int(self.ent_bf_vertices.get())
            density = float(self.ent_bf_density.get()) / 100
            
            if not (1 <= vertices <= 100) or not (0 < density <= 1):
                messagebox.showerror("Input Error", "Vertices: 1-100, Density: 1-100%")
                return
            
            graph = nx.gnp_random_graph(vertices, density, seed=42)
            for (u, v) in graph.edges():
                graph[u][v]['weight'] = np.random.randint(1, 20)
            
            start = 0
            lengths = nx.single_source_bellman_ford_path_length(graph, start, weight='weight')
            
            report = f"BELLMAN-FORD ALL-PAIRS ANALYSIS\n" + "="*60 + "\n\n"
            report += f"Source Node: {start}\n\n"
            report += f"Shortest Distances to All Nodes:\n"
            for node in sorted(lengths.keys())[:20]:
                report += f"  Node {node}: {lengths[node]:.2f}\n"
            
            TextWindow(self.root, "Bellman-Ford Results", report)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ========================================================================
    # FORD-FULKERSON MAXIMUM FLOW
    # ========================================================================
    def show_ford_fulkerson_module(self):
        self.clear()
        self._header("Maximum Flow — Ford-Fulkerson Algorithm")

        outer, inner = make_card(self.root, pad=20)
        outer.pack(padx=50, pady=15, fill="both", expand=True)

        help_frame = tk.Frame(inner, bg=C_HELP_BG, bd=1, relief="solid")
        help_frame.pack(fill="x", pady=(0, 15))
        tk.Label(help_frame, text="FORD-FULKERSON MAXIMUM FLOW PARAMETERS:\n"
                                 "• Number of Vertices: Range 1-100\n"
                                 "• Graph Density: Edge percentage (1-100%)\n"
                                 "Computes maximum flow in a network",
                 font=("Arial", 10, "bold"), fg=C_NAVY, bg=C_HELP_BG, justify="left", anchor="w", padx=15, pady=8).pack(fill="x")

        f_inputs = tk.Frame(inner, bg=C_BG)
        f_inputs.pack(fill="x", padx=10, pady=10)

        tk.Label(f_inputs, text="Number of Vertices:", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=0, column=0, sticky="w", pady=8)
        self.ent_ff_vertices = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_ff_vertices.insert(0, "10")
        self.ent_ff_vertices.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(f_inputs, text="Graph Density (%):", font=("Arial", 11, "bold"), bg=C_BG, fg=C_NAVY).grid(row=1, column=0, sticky="w", pady=8)
        self.ent_ff_density = tk.Entry(f_inputs, width=55, font=("Consolas", 12), highlightbackground=C_ROSE, highlightthickness=1)
        self.ent_ff_density.insert(0, "30")
        self.ent_ff_density.grid(row=1, column=1, padx=15, pady=8)

        f_btns = tk.Frame(inner, bg=C_BG)
        f_btns.pack(fill="x", padx=10, pady=20)

        success_btn(f_btns, "Generate & Solve Ford-Fulkerson", self._solve_ford_fulkerson).pack(side="left", padx=25)

        back_btn(self.root, self.show_main_menu).pack(side="bottom", pady=20)

    def _solve_ford_fulkerson(self):
        try:
            vertices = int(self.ent_ff_vertices.get())
            density = float(self.ent_ff_density.get()) / 100
            
            if not (1 <= vertices <= 100) or not (0 < density <= 1):
                messagebox.showerror("Input Error", "Vertices: 1-100, Density: 1-100%")
                return
            
            graph = nx.gnp_random_graph(vertices, density, seed=42)
            for (u, v) in graph.edges():
                graph[u][v]['weight'] = np.random.randint(1, 20)
            
            G = nx.DiGraph(graph)
            for (u, v) in G.edges():
                G[u][v]['capacity'] = G[u][v]['weight']
            
            start, end = 0, min(vertices-1, 5)
            flow_value, flow_dict = nx.maximum_flow(G, start, end, capacity='capacity')
            
            report = f"FORD-FULKERSON MAXIMUM FLOW ANALYSIS\n" + "="*60 + "\n\n"
            report += f"Flow Network: Source {start} → Sink {end}\n"
            report += f"Maximum Flow Value: {flow_value:.2f}\n\n"
            
            TextWindow(self.root, "Ford-Fulkerson Results", report)
            
            fig = Figure(figsize=(12, 9), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            pos = nx.spring_layout(G, seed=42)
            nx.draw_networkx_nodes(G, pos, node_color=C_LIGHT_ROSE, node_size=500, ax=ax)
            nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax, arrows=True, arrowsize=20, edge_color=C_NAVY)
            flow_edges = [(u, v) for u in flow_dict for v in flow_dict[u] if flow_dict[u][v] > 0]
            nx.draw_networkx_edges(G, pos, edgelist=flow_edges, edge_color=C_ROSE, width=2, ax=ax, arrows=True, arrowsize=20)
            nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)
            ax.set_title(f'Ford-Fulkerson: Max Flow = {flow_value:.0f}', fontsize=16, fontweight='bold', color=C_NAVY)
            ax.axis('off')
            FigureWindow(self.root, fig, "Ford-Fulkerson Maximum Flow Visualization")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ============================================================================
# LANCEMENT
# ============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = ElectricalEngineeringApp(root)
    root.mainloop()

