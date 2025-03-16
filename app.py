from ant_colony import AntColony
from differential_evolution import DifferentialEvolution
from genetic_algorithm import GeneticAlgorithm
from particle_swarm import ParticleSwarm

def main():

    sheet_width = 200
    sheet_height = 100

    recortes_disponiveis = [
        {"tipo": "retangular", "largura": 29, "altura": 29, "x": 1, "y": 1, "rotacao": 0},
        {"tipo": "retangular", "largura": 29, "altura": 29, "x": 31, "y": 1, "rotacao": 0},
        {"tipo": "retangular", "largura": 29, "altura": 29, "x": 1, "y": 31, "rotacao": 0},
        {"tipo": "retangular", "largura": 29, "altura": 29, "x": 1, "y": 69, "rotacao": 0},
        {"tipo": "retangular", "largura": 139, "altura": 29, "x": 60, "y": 70, "rotacao": 0},
        {"tipo": "retangular", "largura": 60, "altura": 8, "x": 66, "y": 52, "rotacao": 0},
        {"tipo": "retangular", "largura": 44, "altura": 4, "x": 117, "y": 39, "rotacao": 0},
        {"tipo": "diamante", "largura": 29, "altura": 48, "x": 32, "y": 31, "rotacao": 0},
        {"tipo": "diamante", "largura": 29, "altura": 48, "x": 62, "y": 2, "rotacao": 0},
        {"tipo": "diamante", "largura": 29, "altura": 48, "x": 94, "y": 2, "rotacao": 0},
        {"tipo": "circular", "r": 16, "x": 124, "y": 2},
        {"tipo": "circular", "r": 16, "x": 158, "y": 2}
    ]

    ps_optimizer = ParticleSwarm(num_particles=50, num_iterations=100, dim=len(recortes_disponiveis),
                                 sheet_width=sheet_width, sheet_height=sheet_height, recortes_disponiveis=recortes_disponiveis)
    print("Running Particle Swarm Optimization...")
    ps_optimized_layout = ps_optimizer.optimize_and_display()

    print("Particle Swarm Optimized Layout:")
    for item in ps_optimized_layout or []:
        print(item)

if __name__ == "__main__":
    main()