import random
import copy
from common.layout_display import LayoutDisplayMixin

class ParticleSwarm(LayoutDisplayMixin):
    def __init__(self, num_particles, num_iterations, dim, sheet_width, sheet_height, recortes_disponiveis):
        """
        Inicializa o otimizador Particle Swarm.
        :param num_particles: Número de partículas.
        :param num_iterations: Número de iterações.
        :param dim: Dimensionalidade do problema.
        :param sheet_width: Largura da folha.
        :param sheet_height: Altura da folha.
        :param recortes_disponiveis: Lista de recortes disponíveis (estrutura JSON).
        """
        self.num_particles = num_particles
        self.num_iterations = num_iterations
        self.dim = dim
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.initial_layout = recortes_disponiveis
        self.particles = []
        self.global_best_position = None
        self.global_best_fitness = float('inf')
        self.optimized_layout = None
        print("Particle Swarm Optimization Inicializado.")

    def initialize_particles(self):
        """ Inicializa partículas com posições e velocidades aleatórias. """
        for shape in self.initial_layout:
            position = self.random_position(shape)
            velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
            particle = {
                "position": position,
                "velocity": velocity,
                "best_position": position,
                "best_fitness": float('inf'),
                "shape": shape,
                "fitness": float('inf')
            }
            self.particles.append(particle)

    def random_position(self, shape):
        """ Gera uma posição aleatória dentro dos limites da folha para o recorte dado. """
        if shape["tipo"] == "retangular":
            x = random.uniform(0, self.sheet_width - shape["largura"])
            y = random.uniform(0, self.sheet_height - shape["altura"])
        elif shape["tipo"] == "circular":
            x = random.uniform(0, self.sheet_width - shape["r"] * 2)
            y = random.uniform(0, self.sheet_height - shape["r"] * 2)
        elif shape["tipo"] == "diamante":
            x = random.uniform(0, self.sheet_width - shape["largura"])
            y = random.uniform(0, self.sheet_height - shape["altura"])
        else:
            x, y = 0, 0
        return [x, y]

    def clamp_position(self, position, shape):
        """ Garante que a posição do recorte permaneça dentro dos limites da folha. """
        x, y = position
        if shape["tipo"] == "retangular":
            x = max(0, min(x, self.sheet_width - shape["largura"]))
            y = max(0, min(y, self.sheet_height - shape["altura"]))
        elif shape["tipo"] == "circular":
            x = max(0, min(x, self.sheet_width - shape["r"] * 2))
            y = max(0, min(y, self.sheet_height - shape["r"] * 2))
        elif shape["tipo"] == "diamante":
            x = max(0, min(x, self.sheet_width - shape["largura"]))
            y = max(0, min(y, self.sheet_height - shape["altura"]))
        return [x, y]

    def get_bounding_box(self, particle):
        """ Retorna a caixa delimitadora do recorte baseado em sua posição e dimensões. """
        x, y = particle["position"]
        shape = particle["shape"]
        if shape["tipo"] in ["retangular", "diamante"]:
            return (x, y, x + shape["largura"], y + shape["altura"])
        elif shape["tipo"] == "circular":
            return (x, y, x + shape["r"] * 2, y + shape["r"] * 2)
        else:
            return (x, y, x, y)

    def boxes_overlap(self, box1, box2):
        """ Verifica se duas caixas delimitadoras se sobrepõem.
        
        Cada caixa é definida como uma tupla (left, top, right, bottom).
        """
        left1, top1, right1, bottom1 = box1
        left2, top2, right2, bottom2 = box2
        # Se uma caixa estiver inteiramente à esquerda, à direita, acima ou abaixo da outra, não há sobreposição.
        return not (right1 <= left2 or right2 <= left1 or bottom1 <= top2 or bottom2 <= top1)

    def get_width(self, particle):
        """ Retorna a largura efetiva do recorte. """
        shape = particle["shape"]
        if shape["tipo"] in ["retangular", "diamante"]:
            return shape["largura"]
        elif shape["tipo"] == "circular":
            return shape["r"] * 2
        return 0

    def get_height(self, particle):
        """ Retorna a altura efetiva do recorte. """
        shape = particle["shape"]
        if shape["tipo"] in ["retangular", "diamante"]:
            return shape["altura"]
        elif shape["tipo"] == "circular":
            return shape["r"] * 2
        return 0

    def calculate_fitness(self, particle):
        """ Função de fitness que penaliza recortes fora dos limites e sobreposição entre recortes. """
        fitness = 0
        x, y = particle["position"]
        shape = particle["shape"]

        # Penaliza se o recorte estiver fora dos limites da folha
        if shape["tipo"] == "retangular":
            if (x + shape["largura"] > self.sheet_width or y + shape["altura"] > self.sheet_height):
                fitness += 1000
        elif shape["tipo"] == "circular":
            if (x + shape["r"] * 2 > self.sheet_width or y + shape["r"] * 2 > self.sheet_height):
                fitness += 1000
        elif shape["tipo"] == "diamante":
            if (x + shape["largura"] > self.sheet_width or y + shape["altura"] > self.sheet_height):
                fitness += 1000

        # Verifica sobreposição com outros recortes
        current_box = self.get_bounding_box(particle)
        for other in self.particles:
            if other is particle:
                continue
            other_box = self.get_bounding_box(other)
            if self.boxes_overlap(current_box, other_box):
                fitness += 1000

        return fitness

    def evaluate_particles(self):
        """ Avalia o fitness e atualiza os melhores individuais e global. """
        for particle in self.particles:
            fitness = self.calculate_fitness(particle)
            particle["fitness"] = fitness

            if fitness < particle["best_fitness"]:
                particle["best_fitness"] = fitness
                particle["best_position"] = copy.deepcopy(particle["position"])

            if fitness < self.global_best_fitness:
                self.global_best_fitness = fitness
                self.global_best_position = copy.deepcopy(particle["position"])

    def update_velocity(self):
        """ Atualiza a velocidade de cada partícula, incluindo uma força repulsiva para evitar colisões. """
        w = 0.5  # Peso de inércia
        c1 = 1.5  # Parâmetro cognitivo
        c2 = 1.5  # Parâmetro social
        repulsive_factor = 0.7  # Fator de escala para a força repulsiva

        for i, particle in enumerate(self.particles):
            # Atualização básica da velocidade
            for d in range(2):  # dimensões x e y
                cognitive = c1 * random.random() * (particle["best_position"][d] - particle["position"][d])
                social = c2 * random.random() * (self.global_best_position[d] - particle["position"][d])
                particle["velocity"][d] = w * particle["velocity"][d] + cognitive + social

            # Verifica colisões com os demais recortes e aplica força repulsiva
            for j, other in enumerate(self.particles):
                if i == j:
                    continue
                if self.boxes_overlap(self.get_bounding_box(particle), self.get_bounding_box(other)):
                    center_particle = [
                        particle["position"][0] + self.get_width(particle) / 2,
                        particle["position"][1] + self.get_height(particle) / 2
                    ]
                    center_other = [
                        other["position"][0] + self.get_width(other) / 2,
                        other["position"][1] + self.get_height(other) / 2
                    ]
                    repulsive_vector = [
                        center_particle[0] - center_other[0],
                        center_particle[1] - center_other[1]
                    ]
                    particle["velocity"][0] += repulsive_factor * repulsive_vector[0]
                    particle["velocity"][1] += repulsive_factor * repulsive_vector[1]

    def update_position(self):
        """ Atualiza a posição de cada partícula com base em sua velocidade. """
        for particle in self.particles:
            new_position = [
                particle["position"][0] + particle["velocity"][0],
                particle["position"][1] + particle["velocity"][1]
            ]
            particle["position"] = self.clamp_position(new_position, particle["shape"])

    def get_best_solution(self):
        """ Compila o layout otimizado baseado nas melhores posições encontradas. """
        layout = []
        for particle in self.particles:
            shape = copy.deepcopy(particle["shape"])
            shape["x"], shape["y"] = particle["best_position"]
            layout.append(shape)
        return layout

    def run(self):
        """ Executa o loop principal do algoritmo PSO. """
        self.initialize_particles()
        for iteration in range(self.num_iterations):
            self.evaluate_particles()
            self.update_velocity()
            self.update_position()
        self.optimized_layout = self.get_best_solution()
        return self.optimized_layout

    def optimize_and_display(self):
        """ Exibe o layout inicial, executa a otimização e exibe o layout otimizado. """
        self.display_layout(self.initial_layout, title="Initial Layout - Particle Swarm")
        self.optimized_layout = self.run()
        self.display_layout(self.optimized_layout, title="Optimized Layout - Particle Swarm")
        return self.optimized_layout
