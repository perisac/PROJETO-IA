import math
import random

from common.layout_display import LayoutDisplayMixin

class ParticleSwarm(LayoutDisplayMixin):
    def __init__(self, num_particles, num_iterations, dim, sheet_width, sheet_height, recortes_disponiveis, fixed_velocity=0.5):
        self.num_particles = num_particles
        self.num_iterations = num_iterations
        self.dim = dim
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.initial_layout = recortes_disponiveis
        self.optimized_layout = None
        self.particles = []
        self.fixed_velocity = fixed_velocity
        self.global_best_position = None
        self.global_best_value = float('inf')
        print("Particle Swarm Optimization Initialized.")

    def initialize_particles(self):
        self.particles = []
        for _ in range(self.num_particles):
            position = [(random.uniform(0, self.sheet_width), random.uniform(0, self.sheet_height)) for _ in range(len(self.initial_layout))]
            velocity = [(self.fixed_velocity, self.fixed_velocity) for _ in range(len(self.initial_layout))]
            particle = {
                'position': position,
                'velocity': velocity,
                'best_position': position,
                'best_value': float('inf')
            }
            self.particles.append(particle)

    def calculate_layout_value(self, layout_position):
        total_sheet_area = self.sheet_width * self.sheet_height
        total_recortes_area = 0
        overlap_penalty = 0

        for i, (x1, y1) in enumerate(layout_position):
            recorte1 = self.initial_layout[i]

            # Calcular área do recorte 1
            if recorte1['tipo'] == 'retangular':
                recorte1_width = recorte1['largura']
                recorte1_height = recorte1['altura']
                recorte1_area = recorte1_width * recorte1_height
            elif recorte1['tipo'] == 'diamante':
                recorte1_width = recorte1['largura']
                recorte1_height = recorte1['altura']
                recorte1_area = (recorte1_width * recorte1_height) / 2  # Área do diamante
            elif recorte1['tipo'] == 'circular':
                recorte1_r = recorte1['r']
                recorte1_area = math.pi * (recorte1_r ** 2)  # Área do círculo
            else:
                recorte1_area = 0

            # Verificar se o recorte 1 está fora da folha
            if x1 + recorte1_width > self.sheet_width or y1 + recorte1_height > self.sheet_height:
                total_recortes_area += recorte1_area * 100
                continue

            total_recortes_area += recorte1_area

            # Verificar sobreposição entre recortes
            for j, (x2, y2) in enumerate(layout_position):
                if i >= j:
                    continue

                recorte2 = self.initial_layout[j]

                # Calcular área do recorte 2
                if recorte2['tipo'] == 'retangular':
                    recorte2_width = recorte2['largura']
                    recorte2_height = recorte2['altura']
                elif recorte2['tipo'] == 'diamante':
                    recorte2_width = recorte2['largura']
                    recorte2_height = recorte2['altura']
                elif recorte2['tipo'] == 'circular':
                    recorte2_r = recorte2['r']
                    recorte2_width = recorte2_height = recorte2_r * 2  # Usamos o diâmetro do círculo
                else:
                    recorte2_width = recorte2_height = 0

                # Verificar sobreposição entre recorte1 e recorte2
                if self.is_overlapping(x1, y1, recorte1_width, recorte1_height, x2, y2, recorte2_width, recorte2_height, recorte1, recorte2):
                    overlap_penalty += 100 * 1000

            desperdicio = total_sheet_area - total_recortes_area
            return desperdicio + overlap_penalty

    def is_overlapping(self, x1, y1, w1, h1, x2, y2, w2, h2, recorte1, recorte2):
        # Verificação de sobreposição entre círculos
        if recorte1['tipo'] == 'circular' and recorte2['tipo'] == 'circular':
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            return distance < (recorte1['r'] + recorte2['r'])

        # Verificação de sobreposição entre retângulos, diamantes ou outras formas
        no_overlap = (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
        return not no_overlap

    def update_velocity(self, w=0.5, c1=1.5, c2=1.5):
        for particle in self.particles:
            new_velocity = []
            for i, (pos_x, pos_y) in enumerate(particle['position']):
                v_x, v_y = particle['velocity'][i]
                
                r1 = random.random()  # Número aleatório entre 0 e 1
                r2 = random.random()  # Número aleatório entre 0 e 1
                    
                # Verifique se o tamanho de 'personal_best' e 'global_best' são consistentes
                personal_best = particle['best_position'][i] if i < len(particle['best_position']) else (0, 0)
                global_best = self.global_best_position[i] if self.global_best_position and i < len(self.global_best_position) else (0, 0)

                # Calcular a nova velocidade para x e y
                vel_x = (w * v_x) + (c1 * r1 * (personal_best[0] - pos_x)) + (c2 * r2 * (global_best[0] - pos_x))
                vel_y = (w * v_y) + (c1 * r1 * (personal_best[1] - pos_y)) + (c2 * r2 * (global_best[1] - pos_y))
                new_velocity.append((vel_x, vel_y))

            particle['velocity'] = new_velocity

    def update_position(self):
        for particle in self.particles:
            new_position = []
            for i, (pos_x, pos_y) in enumerate(particle['position']):
                vel_x, vel_y = particle['velocity'][i]
                new_x = pos_x + vel_x
                new_y = pos_y + vel_y

                # Garantir que a nova posição não ultrapasse os limites
                recorte = self.initial_layout[i]
                recorte_width = recorte['largura'] if recorte['tipo'] != 'circular' else recorte['r'] * 2
                recorte_height = recorte['altura'] if recorte['tipo'] != 'circular' else recorte['r'] * 2

                new_x = min(max(new_x, 0), self.sheet_width - recorte_width)
                new_y = min(max(new_y, 0), self.sheet_height - recorte_height)

                new_position.append((new_x, new_y))

            particle['position'] = new_position

    def get_best_solution(self):
        for particle in self.particles:
            current_value = self.calculate_layout_value(particle['position'])
            if current_value < particle['best_value']:
                particle['best_value'] = current_value
                particle['best_position'] = particle['position']

            if current_value < self.global_best_value:
                self.global_best_value = current_value
                self.global_best_position = particle['position']

    def run(self):
        self.initialize_particles()

        for _ in range(self.num_iterations):
            self.get_best_solution()
            self.update_velocity()
            self.update_position()

        self.optimized_layout = self.global_best_position
        return self.optimized_layout

    def optimize_and_display(self):
        """
        Displays the initial layout, runs the optimization, and then displays the optimized layout.
        """
        # Exibir layout inicial
        self.display_layout(self.initial_layout, title="Initial Layout - Particle Swarm")

        # Rodar a otimização (isso deve atualizar self.optimized_layout)
        self.optimized_layout = self.run()

        # Atualizar self.optimized_layout para conter dicionários completos (com 'x', 'y' e outros atributos)
        optimized_layout_with_recortes = []
        for i, (x, y) in enumerate(self.optimized_layout):
            recorte = self.initial_layout[i].copy()  # Copia o recorte original
            recorte["x"] = x  # Atualiza a posição x
            recorte["y"] = y  # Atualiza a posição y
            optimized_layout_with_recortes.append(recorte)  # Adiciona o recorte completo

        # Exibir layout otimizado
        self.display_layout(optimized_layout_with_recortes, title="Optimized Layout - Particle Swarm")

        return optimized_layout_with_recortes