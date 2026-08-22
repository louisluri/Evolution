"""Simulates natural selection in the fictional Neebler population."""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
import random
import numpy as np

def on_press(event):
    if event.key == ' ':
        global is_paused
        is_paused = not is_paused

def get_colors(dna_matrix):

    dna_matrix = np.atleast_2d(dna_matrix)
    # Create Empty Color Array (N rows, 3 columns for RGB)
    colors = np.zeros((len(dna_matrix), 3))

    # RED Channel: Influenced by Size (idx0) and Diet/Carnivore (idx5)
    # Big meat eaters will tend toward Red/Magenta.Small herbivores toward Cyan.
    colors[:, 0] = scale_gene(dna_matrix[:, 0] + dna_matrix[:, 5], 1, k=1.5)

    # GREEN Channel: Influenced by Speed (idx1) and Stealth (idx3)
    # Fast, sneaky neeblers will tend toward Green/Yellow.
    colors[:, 1] = scale_gene(dna_matrix[:, 1] + dna_matrix[:, 3], 1, k=1.5)

    # BLUE Channel: Influenced by Perception (idx2) and Aggression (idx4)
    # Perceptive, Aggressive neeblers will tend toward Blue/Cyan.
    colors[:, 2] = scale_gene(dna_matrix[:, 2] + dna_matrix[:, 4], 1, k=1.5)

    colors = (colors - 0.5) * 1.5 + 0.5  # Extra Contrast
    colors = np.clip(colors, 0, 1) # Ensure valid RGB range

    return colors

def correct_direction(delta, max):
   """takes in a potential change in x or y and adjusts and returns the change to take the shortest path 
   recognizing that you can go around the globe"""
   
   if np.abs(delta) > max / 2:
      if delta > 0:
         delta -= max
      elif delta < 0:
         delta += max

   return delta

def normalize(x, y):
    """Returns the unit vector (length 1) for a given x, y. 
    Handles the case where the vector is (0,0) to prevent division by zero."""

    magnitude = np.sqrt(x**2 + y**2)
    
    if magnitude > 0:
        return x / magnitude, y / magnitude
    else:
        return 0, 0
    
def scale_gene(value, max_output, k=3.0):
    """Maps a gene (around 0) to a positive output value with a cap."""
    # This ensures speed never exceeds 'max_output' even if gene is 1,000,000
    return max_output / (1 + np.exp(-k * value))

def get_win_prob(subject, opponent, is_attacking=False, k=10.0):
   """The probability of one neebler winning a fight aginst another, "is_attacking" refers to the subject neeb"""

   if is_attacking:
      diff = (subject.dna[0] + 0.2) - opponent.dna[0]
   else:
      diff = subject.dna[0] - opponent.dna[0]

   return 1 / (1 + np.exp(-k * diff))

def wants_to_fight(subject, opponent, is_attacking=False):
   """Decides if the Neebler engages based on risk tolerance."""

   win_prob = get_win_prob(subject, opponent, is_attacking=is_attacking)

   return win_prob >= subject.risk_thresh

def update_graphics(neebler_pop, plant_pop, year, year_end=False):
    """
    neebler_pop: List of Neebler objects
    plant_pop:   List of Plant objects
    year:        Current year (int)
    year_end:    Update Histograms/Stats Too?
    """

    if len(neebler_pop) == 0:
        ax_map.set_title(f"Year {year} | EXTINCTION EVENT")
        # Clear the map to show empty world
        ax_neeb.set_offsets(np.c_[[], []])
        ax_eye_L.set_offsets(np.c_[[], []])
        ax_eye_R.set_offsets(np.c_[[], []])
        ax_pupil_L.set_offsets(np.c_[[], []])
        ax_pupil_R.set_offsets(np.c_[[], []])
        return

    foodx = [snack.x for snack in plant_pop]
    foody = [snack.y for snack in plant_pop]
    ax_food.set_offsets(np.c_[foodx, foody])

    # all dna data for plotting
    dna_matrix = np.array([n.dna for n in neebler_pop])
    
    colors = get_colors(dna_matrix)

    x_coords = np.array([neebler.x for neebler in neebler_pop])
    y_coords = np.array([neebler.y for neebler in neebler_pop])
    ax_neeb.set_offsets(np.c_[x_coords, y_coords])
    ax_neeb.set_sizes((dna_matrix[:, 0] + start_size) * increment)
    ax_neeb.set_facecolor(colors)

    ax_eye_L.set_offsets(np.c_[x_coords - (x_offset * (dna_matrix[:, 0] + start_offset)), y_coords + (y_offset * (dna_matrix[:, 0] + start_offset))])
    ax_eye_R.set_offsets(np.c_[x_coords + (x_offset * (dna_matrix[:, 0] + start_offset)), y_coords + (y_offset * (dna_matrix[:, 0] + start_offset))])
    ax_pupil_L.set_offsets(np.c_[x_coords - (x_offset * (dna_matrix[:, 0] + start_offset)), y_coords + (y_offset * (dna_matrix[:, 0] + start_offset))])
    ax_pupil_R.set_offsets(np.c_[x_coords + (x_offset * (dna_matrix[:, 0] + start_offset)), y_coords + (y_offset * (dna_matrix[:, 0] + start_offset))])
    ax_eye_L.set_sizes(((dna_matrix[:, 0] + start_size) * increment) / eye_scale)
    ax_eye_R.set_sizes(((dna_matrix[:, 0] + start_size) * increment) / eye_scale)
    ax_pupil_L.set_sizes(((dna_matrix[:, 0] + start_size) * increment * scale_gene(dna_matrix[:, 2], 1.5)) / pupil_scale)
    ax_pupil_R.set_sizes(((dna_matrix[:, 0] + start_size) * increment * scale_gene(dna_matrix[:, 2], 1.5)) / pupil_scale)

    ax_map.set_xlabel(f"Year {year} | Pop: {len(neebler_pop)} | Plants: {len(plant_pop)}", fontsize=12)

    if year_end:
        # UPDATE HISTOGRAMS
        # List of: (Axis, DNA_Column, Title, Color)
        hist_setup = [
            (ax_size,    0, "Size",       'red'),
            (ax_speed,   1, "Speed",      'blue'),
            (ax_percep,  2, "Perception", 'purple'),
            (ax_stealth, 3, "Stealth",    'gray'),
            (ax_bravery, 4, "Aggression", 'orange'),
            (ax_diet,    5, "Diet",       'green')
        ]

        for ax, col, name, color in hist_setup:
            ax.clear()
            ax.hist(dna_matrix[:, col], bins=25, range=(min(-0.5, min(dna_matrix[:, col])), max(0.5, max(dna_matrix[:, col]))), color=color, alpha=0.7, edgecolor='black')
            ax.set_title(name, fontsize=12, pad=3)
            ax.set_xlim(min(-0.5, min(dna_matrix[:, col])), max(0.5, max(dna_matrix[:, col])))
            ax.set_yticks([])
            ax.grid(True, linestyle='--', color='gray', alpha=0.6)

        mean_dna = np.mean(dna_matrix, axis=0)

        # Get the average DNA for every tribe
        rows = [t[0].round(2).tolist() + [t[1]] for t in tribes.values()] + [mean_dna.round(2).tolist() + [len(neebler_pop)]]
        # Labels for each row
        row_labels = [f"Tribe {t}" for t in tribes.keys()] + ["Average"]

        colors = get_colors(np.vstack([np.array([t[0] for t in tribes.values()]), mean_dna]))

        ax_dna.cla()
        ax_dna.axis('off')

        the_table = ax_dna.table(cellText=rows, 
                         colLabels=columns, 
                         rowLabels=row_labels,
                         loc='center left',
                         cellLoc='center')
        
        # 2. COLOR THE HEADERS (Every Loop)
        for j in range(len(columns)-1):
            cell = the_table[0, j]
            cell.set_facecolor(hist_setup[j][3])
            cell.get_text().set_color('white')
            cell.get_text().set_weight('bold')
        cell = the_table[0, len(columns)-1]
        cell.set_facecolor('brown')
        cell.get_text().set_color('white')
        cell.get_text().set_weight('bold')

        for i in range(len(rows)):
            row_color = (*colors[i], 0.7)

            for j in range(len(columns) + 1):
                # i + 1 because row 0 is the header
                the_table[i + 1, j - 1].set_facecolor(row_color)
        
        
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(9)
        the_table.scale(1, 1.5)

        distances = np.sum((dna_matrix - mean_dna)**2, axis=1)

        std_dev = np.sqrt(np.sum(distances) / (len(distances) - 1))

        global reproduced

        pop_history['rep'].append(reproduced/len(neebler_pop))
        pop_history['std'].append(std_dev)
        pop_history['gen'].append(year)
        pop_history['pop'].append(len(neebler_pop))
        pop_history['plant'].append(len(plant_pop))

        for i, (tribe_id, data) in enumerate(tribes.items()):
            if tribe_id in tribe_plot_history:
                tribe_plot_history[tribe_id][0].append(data[1])
                tribe_plot_history[tribe_id][1].append(year)
                tribe_plot_history[tribe_id][2].append(colors[i])
            else:
                tribe_plot_history[tribe_id] = [[data[1]], [year], [colors[i]]]

            # We need at least 2 points to draw a segment
            if len(tribe_plot_history[tribe_id][0]) > 1:
                x = np.array(tribe_plot_history[tribe_id][1], dtype=float)
                y = np.array(tribe_plot_history[tribe_id][0], dtype=float)
                c = np.array(tribe_plot_history[tribe_id][2], dtype=float)

                # Create segments: [(x0, y0), (x1, y1)], [(x1, y1), (x2, y2)] ...
                points = np.vstack([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)

                # The color of each segment is the color recorded at that year
                # use the colors from the 2nd point of each segment onward
                seg_colors = c[1:]

                # If a collection for this tribe already exists, remove it before adding the new one
                if tribe_id in tribe_plot_lines:
                    tribe_plot_lines[tribe_id].remove()

                # Create the new LineCollection
                lc = LineCollection(segments, colors=seg_colors, linewidths=2, zorder=5)
                tribe_plot_lines[tribe_id] = ax_tribe_line.add_collection(lc)

        all_y_values = []
        all_x_values = []
        # Gather all current data points from all tribes to find min/max
        for t_history in tribe_plot_history.values():
            all_y_values.extend(t_history[0]) # Population counts
            all_x_values.extend(t_history[1]) # Years

        if all_x_values and all_y_values:
            # Set X limit to the current year (plus a little buffer if you want)
            ax_tribe_line.set_xlim(min(all_x_values) - 1, max(all_x_values) + 1)
            
            # Set Y limit to max population found (plus 10% headroom)
            ax_tribe_line.set_ylim(0, max(all_y_values) * 1.1)


        plot_lines['std'].set_data(pop_history['gen'], pop_history['std'])
        plot_lines['rep'].set_data(pop_history['gen'], pop_history['rep'])
        plot_lines['pop'].set_data(pop_history['gen'], pop_history['pop'])
        plot_lines['plant'].set_data(pop_history['gen'], pop_history['plant'])

        ax_div.relim()
        ax_div.autoscale_view()

        ax_tot.relim()
        ax_tot.autoscale_view()

class Neebler:
   def __init__(self, mom_xcoord=None, mom_ycoord=None, parent_dna=None, age=0):
      if mom_xcoord is None and mom_ycoord is None and parent_dna is None:
         self.x = X_MAX * random.random()
         self.y = Y_MAX * random.random()
         self.dna = np.array([np.random.rand() - 0.5, # idx0, size
                              np.random.rand() - 0.5, # idx1, speed
                              np.random.rand() - 0.5, # idx2, perception
                              np.random.rand() - 0.5, # idx3, stealth
                              np.random.rand() - 0.5, # idx4, aggression
                              np.random.rand() - 0.5])# idx5, herb/carn
      elif mom_xcoord is not None and mom_ycoord is not None and parent_dna is not None:
         self.x = (mom_xcoord + (((random.random() * 2) - 1) * born_distance)) % Y_MAX
         self.y = (mom_ycoord + (((random.random() * 2) - 1) * born_distance)) % Y_MAX
         self.dna = np.array([random.gauss(parent_dna[0], mutation_rate), 
                              random.gauss(parent_dna[1], mutation_rate), 
                              random.gauss(parent_dna[2], mutation_rate),
                              random.gauss(parent_dna[3], mutation_rate), 
                              random.gauss(parent_dna[4], mutation_rate), 
                              random.gauss(parent_dna[5], mutation_rate)])
      else: 
         raise ValueError("You tried to create a neebler with inadequate info from the parent")

      self.metabolism = 1 + (2 * np.exp((self.dna[0] * 0.7) + (self.dna[1] * 0.6) + (self.dna[2] * 0.2) + (self.dna[3] * 0.2))) # need this much food to garunteed live and to procreate
      self.sight = scale_gene(self.dna[2], 30)                                 # how far away can this neebler see
      self.speed = scale_gene(self.dna[1], 4)                                  # speed is altered down by high stealth
      self.plant_bonus = scale_gene(-self.dna[5], 2)                           # multiplies with the plant to get the ammount of food rewarded, "digestion"
      self.meat_bonus = 1 + scale_gene(self.dna[5], 6, k=2)**2                          # multiplies with the meat to get the ammount of food rewarded, "digestion"
      self.plant_reserve = 0.47 + scale_gene(self.dna[5], 0.2)                 # what % of the plants must be preserved by this neeb
      self.stealth = scale_gene(-(self.dna[3]-0.25), 1.5)                               # this will multiply with the surrounding neeblers sight
      self.meat = 2 + scale_gene(self.dna[0]-0.3, 6, k=2.0)                           # how much nourishment is offered to a pred that catches this neeb
      self.risk_thresh = scale_gene(-(self.dna[4]-0.2), 0.9, k=4)

      self.age = age                     # how old is this neeb?
      self.food = 0                      # the food it has ate this year
      self.freeze = 0                    # this dictates how many steps the neebler is frozen in place for
      self.tribe = -1

class Plant:
   def __init__(self, xcoord, ycoord):
      self.x = xcoord
      self.y = ycoord

#class Predator:

is_paused = True
reproduced = 0
tribes = {}
tribe_count = 0
tribe_dist = 0.5

# hyperparams
X_MAX = 100
Y_MAX = X_MAX # boundries of our fictional world

# eye ball offsets 
start_offset = 3
x_offset = 0.30 * (np.sqrt(X_MAX)/10)
y_offset = 0.20 * (np.sqrt(X_MAX)/10)
eye_scale = 7
pupil_scale = 50

# neebler size increments on the scatter
start_size = 1.7    # neeblers of size 0 have size start*increment on the plot
increment = 250 / (X_MAX/100)

# pause time
pause = 0.5              # step pause is pause * 0.1

max_age = 10             # max life span

num_neeblers = 80       # starting pop size

carrying_capacity = int(200 * (X_MAX / 100)) # plant foods carrying capacity and starting point
growth_rate = 1.6

interaction_distance = 2 # how far away can they interact with a food/neebler
born_distance = 7        # how far away can a baby be born from their mother (random.random() * born_distance) for x,y
freeze_steps = 2         # steps it takes to interact with something
steps_per_year = 30

mutation_rate = 0.06        # std dev for the baby creation
cannibalism_threshold = 0.3


#get starting neebler pop
neebler_pop = [Neebler(age=random.randint(0,max_age)) for neebler in range(num_neeblers)]

#place them in a tribe
for n in neebler_pop:
    possible_tribes = [] # idx of the possible tribes with the distance
    winning_tribe = False
    for tribe_id, data in tribes.items():
            genetic_diff = np.linalg.norm(np.array(n.dna) - data[0])
            if genetic_diff <= tribe_dist:
                possible_tribes.append([tribe_id, genetic_diff])

    if possible_tribes:
        arr = np.array(possible_tribes)
        winner_idx = np.argmin(arr[:, 1])
        winning_tribe = int(arr[winner_idx, 0])
        tribes[winning_tribe][0] = ((tribes[winning_tribe][0] * tribes[winning_tribe][1]) + n.dna) / (tribes[winning_tribe][1] + 1)
        tribes[winning_tribe][1] += 1
        n.tribe = winning_tribe
    else:
        tribes[tribe_count] = [n.dna, 1]
        n.tribe = tribe_count
        tribe_count += 1

#Initialize food
plant_pop = [Plant(random.random() * X_MAX, random.random() * Y_MAX) for snack in range(carrying_capacity)]

pop_history = {'std': [], 'rep': [], 'gen': [], 'pop': [], 'plant': []}
plot_lines = {}
tribe_plot_lines = {}
tribe_plot_history = {}

#enable interactive mode
plt.ion()
fig1 = plt.figure(figsize=(16, 7.53))
fig2 = plt.figure(figsize=(16, 7.53))

fig1.canvas.mpl_connect('key_press_event', on_press)

gs1 = gridspec.GridSpec(3, 4, figure=fig1, width_ratios=[0.8, 0.8, 1, 1])
gs2 = gridspec.GridSpec(4, 4, figure=fig2, width_ratios=[1, 1, 0.8, 0.8])

ax_tot = fig2.add_subplot(gs2[2:, 2:])
ax_div = fig2.add_subplot(gs2[:2, 2:])
ax_tribe_line = fig2.add_subplot(gs2[2:, :2], facecolor="#dbdace99")
ax_dna = fig2.add_subplot(gs2[:2, :2])
plot_lines['rep'], = ax_div.plot([], [], linestyle='-', label='% Reproduced', color='g')
plot_lines['std'], = ax_div.plot([], [], linestyle='-', label='Diversity (std)', color='m')
plot_lines['pop'], = ax_tot.plot([], [], linestyle='-', label='Total Population', color='k')
plot_lines['plant'], = ax_tot.plot([], [], linestyle='-', label='Plant Pop', color='darkgreen')
ax_tot.plot([0], [0])
ax_dna.set_xticks([])
ax_dna.set_yticks([])

handles, labels = ax_div.get_legend_handles_labels()
ax_div.legend(handles, labels, loc='upper left', fontsize=9)

handles, labels = ax_tot.get_legend_handles_labels()
ax_tot.legend(handles, labels, loc='upper left', fontsize=9)

ax_tot.grid(True) # Add a grid for easier viewing
ax_div.grid(True)
ax_tribe_line.grid(True)
ax_tot.set_xlabel('Year', fontweight='bold')
ax_tribe_line.set_xlabel('Year', fontweight='bold')

for spine in ax_dna.spines.values():
    spine.set_linewidth(0)

# Headers for genes table
columns = ["Size", "Speed", "Percep", "Stealth", "Agro", "Diet", "Count"]

ax_map = fig1.add_subplot(gs1[:, 2:], facecolor="#dbdace99")
ax_map.set_title("Neebler World")
ax_map.set_xlim(0, X_MAX)
ax_map.set_ylim(0, Y_MAX)
ax_map.set_xticks([])
ax_map.set_yticks([])
# Select all four sides of the plot border
for spine in ax_map.spines.values():
    spine.set_linewidth(3)  # Increase this number for a thicker border
    spine.set_edgecolor('black') # change the border color here

ax_map.set_aspect('equal', adjustable='box')

#start the map plot
ax_neeb = ax_map.scatter([], [], edgecolors='grey', linewidths=0.2)
ax_food = ax_map.scatter([], [], color='darkgreen', marker='s',alpha=0.4,label='Plant Resource', zorder=0)

#plot fun little eyes for the neebs
ax_eye_L = ax_map.scatter([], [], c='white', edgecolors='k', linewidths=0.2, zorder=2)
ax_eye_R = ax_map.scatter([], [], c='white', edgecolors='k', linewidths=0.2, zorder=2)
ax_pupil_L = ax_map.scatter([], [], c='black', zorder=3)
ax_pupil_R = ax_map.scatter([], [], c='black', zorder=3)

# The 6 Histograms (Right Half)
ax_size    = fig1.add_subplot(gs1[0, 0])
ax_speed   = fig1.add_subplot(gs1[0, 1])# Row 0

ax_percep  = fig1.add_subplot(gs1[1, 0])
ax_stealth = fig1.add_subplot(gs1[1, 1])# Row 1

ax_bravery = fig1.add_subplot(gs1[2, 0])
ax_diet    = fig1.add_subplot(gs1[2, 1])# Row 2


plt.tight_layout()
fig1.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
fig2.subplots_adjust(left=0.05, right=0.95, bottom=0.07, top=0.98)

plt.draw()


for year in range(250):
    plt.pause(pause)

    # start each round with new food grown
    new_plant_count = int(growth_rate * len(plant_pop) * (1 - (len(plant_pop) / carrying_capacity)))
    plant_pop.extend(Plant(random.random() * X_MAX, random.random() * Y_MAX) for snack in range(new_plant_count))
    start_year_plants = len(plant_pop)

    #plot
    update_graphics(neebler_pop, plant_pop, year, year_end=True)

    plt.pause(pause)


    #create a base of random directions to start the next round
    theta = np.random.uniform(0, 2 * np.pi, size=len(neebler_pop))


    # each year consists of some number of time steps for neeblers to find food and mate
    for time_step in range(steps_per_year):

        while is_paused:
            plt.pause(0.1)

        #initialize the step size array
        speeds = np.array([neebler.speed for neebler in neebler_pop])

        # moving with purpose
        for i, neebler in enumerate(neebler_pop):

            if neebler.freeze <= 0:

                closest_pred_dist = False
                closest_prey_dist = float('inf')
                closest_plant_dist = float('inf')
                closest_prey_size = 0
            
                prey_dx = False
                prey_dy = False
                pred_dx = []
                pred_dy = []
                plant_dx = False
                plant_dy = False
                tribe_dx = []
                tribe_dy = []

                brave_prey = False

                #loop through each other neebler once to see if there is any pull on the subjects direction
                for neebler2 in neebler_pop:
                    deltax_min = correct_direction(neebler2.x - neebler.x, X_MAX)
                    deltay_min = correct_direction(neebler2.y - neebler.y, Y_MAX)
                    current_distance = np.sqrt((deltax_min)**2 + (deltay_min)**2)
                    genetic_diff = np.linalg.norm(np.array(neebler.dna) - np.array(neebler2.dna))
                    wants_fight = wants_to_fight(neebler, neebler2, is_attacking=True)

                    if genetic_diff <= cannibalism_threshold and current_distance <= neebler.sight:
                        tribe_dx.append(deltax_min)
                        tribe_dy.append(deltay_min)

                    if neebler.sight * neebler2.stealth >= current_distance:

                        # check for all possible prey
                        if wants_fight and cannibalism_threshold < genetic_diff and current_distance < closest_prey_dist and neebler.food < neebler.metabolism:

                            prey_dx = deltax_min
                            prey_dy = deltay_min

                            closest_prey_dist = current_distance
                            closest_prey_size = neebler2.dna[0]

                            if wants_to_fight(neebler2, neebler, is_attacking=True) and neebler2.food < neebler2.metabolism:
                                brave_prey = True
                            else:
                                brave_prey = False

                            break
                        
                        #check if the neebler is a potential predator to run from
                        elif (cannibalism_threshold < genetic_diff and not 
                              wants_to_fight(neebler, neebler2, is_attacking=False) and wants_to_fight(neebler2, neebler, is_attacking=True)):

                            pred_dx.append(deltax_min)
                            pred_dy.append(deltay_min)

                            if current_distance < closest_pred_dist:
                                closest_pred_dist = current_distance

                if neebler.food < neebler.metabolism and (len(plant_pop))/ start_year_plants > neebler.plant_reserve:
                    for s, snack in enumerate(plant_pop):
                        deltax_min = correct_direction(snack.x - neebler.x, X_MAX)
                        deltay_min = correct_direction(snack.y - neebler.y, Y_MAX)
                        current_distance = np.sqrt((deltax_min)**2 + (deltay_min)**2)

                        if neebler.sight >= current_distance and current_distance < closest_plant_dist:

                            plant_dx = deltax_min
                            plant_dy = deltay_min
                            closest_plant_dist = current_distance

                flee_x, flee_y = 0, 0
                if pred_dx and pred_dy:
                    for index in range(len(pred_dx)):
                        pred_dist = np.sqrt((pred_dx[index])**2 + (pred_dy[index])**2)
                        weight = 1 / (pred_dist**2 + 0.01)

                        flee_x -= pred_dx[index] * weight
                        flee_y -= pred_dy[index] * weight


                prey_dx = prey_dx if prey_dx else 0
                prey_dy = prey_dy if prey_dy else 0
                prey_dx, prey_dy = normalize(prey_dx, prey_dy)

                pred_dx = flee_x
                pred_dy = flee_y
                pred_dx, pred_dy = normalize(pred_dx, pred_dy)

                plant_dx = plant_dx if plant_dx else 0
                plant_dy = plant_dy if plant_dy else 0
                plant_dx, plant_dy = normalize(plant_dx, plant_dy)

                tribe_dx = np.mean(tribe_dx) if tribe_dx else 0
                tribe_dy = np.mean(tribe_dy) if tribe_dy else 0
                tribe_dx, tribe_dy = normalize(tribe_dx, tribe_dy)

                pred_weight = (4 / (closest_pred_dist**2 + 0.01)) * scale_gene(neebler.dna[4], 1)

                if neebler.plant_bonus > (neebler.meat_bonus * closest_prey_size) and (plant_dx, plant_dy) != (0, 0):
                    prey_weight = 0
                    plant_weight = 2
                else:
                    plant_weight = 0
                    prey_weight = 2

                if neebler.food >= neebler.metabolism and (pred_dx, pred_dy) == (0, 0):
                    tribe_weight = 2
                else: 
                    tribe_weight = 0

                if brave_prey and prey_weight > 0:
                    speeds[i] = min(speeds[i] * 1.5, closest_prey_dist/1.5)
                elif prey_weight > 0:
                    speeds[i] *= 1.5

                deltax = (prey_dx * prey_weight) + (plant_dx * plant_weight) + (pred_dx * pred_weight) + (tribe_dx * tribe_weight)
                deltay = (prey_dy * prey_weight) + (plant_dy * plant_weight) + (pred_dy * pred_weight) + (tribe_dy * tribe_weight)
                    
                if (deltax, deltay) != (0, 0):
                    theta[i] = np.atan2(deltay, deltax)


        #find out how far each needs to move in x and y
        dx = speeds * np.cos(theta)
        dy = speeds * np.sin(theta)

        #update pos wrapping around the map if needed
        for i, neebler in enumerate(neebler_pop):
            if neebler.freeze > 0:
                neebler.freeze -= 1
            else:
                neebler.x = (neebler.x + dx[i]) % X_MAX
                neebler.y = (neebler.y + dy[i]) % Y_MAX


        #interaction
        # each neebler can try to eat the plants near them
        dead_plants = []
        for s, snack in enumerate(plant_pop):
            nearby_neebs_i = []    #list of indicies

            for i, neebler in enumerate(neebler_pop):
                distance = np.sqrt((correct_direction(neebler.x - snack.x, X_MAX))**2 + (correct_direction(neebler.y - snack.y, Y_MAX))**2)

                if (distance <= interaction_distance and neebler.freeze <= 0 and neebler.food < neebler.metabolism and
                        ((len(plant_pop) - len(dead_plants))/ start_year_plants) > neebler.plant_reserve):
                
                        nearby_neebs_i.append(i)

            if nearby_neebs_i:
                winning_neebler = random.choice(nearby_neebs_i)
                neebler_pop[winning_neebler].food += neebler_pop[winning_neebler].plant_bonus
                neebler_pop[winning_neebler].freeze = freeze_steps
                dead_plants.append(s)

        #plants that got ate get removed from plant pop
        for i in sorted(dead_plants, reverse=True):
            plant_pop.pop(i)

            
        # each nearby neebler has a chance to be eat them or mate
        death_indicies = []
        for i, neebler in enumerate(neebler_pop):

            #loop through each other neebler once
            for i2, neebler2 in enumerate(neebler_pop):

                if i in death_indicies:
                    break

                if interaction_distance >= np.sqrt((correct_direction(neebler.x - neebler2.x, X_MAX))**2 + (correct_direction(neebler.y - neebler2.y, Y_MAX))**2):
                    genetic_diff = np.linalg.norm(np.array(neebler.dna) - np.array(neebler2.dna))

                    # check if any nearby predators eat the subject neeb
                    if (cannibalism_threshold < genetic_diff and wants_to_fight(neebler2, neebler, is_attacking=True) and neebler2.food < neebler2.metabolism and
                        i2 not in death_indicies and neebler2.freeze <= 0 and i not in death_indicies):

                        if ((neebler.food < neebler.metabolism and wants_to_fight(neebler, neebler2, is_attacking=True)) or
                            (neebler.food >= neebler.metabolism and wants_to_fight(neebler, neebler2, is_attacking=False))):
                            win_chance = get_win_prob(neebler2, neebler, is_attacking=False)
                        else:
                            win_chance = get_win_prob(neebler2, neebler, is_attacking=True)

                        if random.random() < win_chance:
                            neebler2.food += neebler.meat * neebler2.meat_bonus
                            neebler2.freeze = freeze_steps
                            death_indicies.append(i)
                            break
                        else:
                            neebler.food += neebler2.meat * neebler.meat_bonus
                            neebler.freeze = freeze_steps
                            death_indicies.append(i2)
                            break


        for i in sorted(death_indicies, reverse=True):
            if tribes[neebler_pop[i].tribe][1] != 1:
                tribes[neebler_pop[i].tribe][0] = ( (tribes[neebler_pop[i].tribe][0] * tribes[neebler_pop[i].tribe][1]) - neebler_pop[i].dna ) / (tribes[neebler_pop[i].tribe][1] - 1)
            tribes[neebler_pop[i].tribe][1] -= 1
            neebler_pop.pop(i)

        theta = np.delete(theta, death_indicies)


        #plot
        update_graphics(neebler_pop, plant_pop, year, year_end=False)

        plt.pause(pause*0.1)


    reproduced = 0
    death_indicies = []
    new_babies = []
    # end of year loop, check for starved/ old neebs and new neeblers are born
    for i, neebler in enumerate(neebler_pop):
        # age each neebler by one year
        neebler.age += 1
        if neebler.age >= max_age:
            death_indicies.append(i)
            continue
        elif neebler.food < neebler.metabolism:
            survival_chance = neebler.food / neebler.metabolism
            if random.random() > survival_chance:
                death_indicies.append(i)
                continue

        if neebler.food >= neebler.metabolism:
            reproduced += 1
            if random.random() < scale_gene(-neebler.dna[0], 0.5):
                new_babies.append(Neebler(neebler.x, neebler.y, neebler.dna))
                new_babies.append(Neebler(neebler.x, neebler.y, neebler.dna))
            else:
                new_babies.append(Neebler(neebler.x, neebler.y, neebler.dna))
        neebler.food = 0

    for b in new_babies:
        possible_tribes = [] # idx of the possible tribes with the distance
        winning_tribe = False
        for tribe_id, data in tribes.items():
            genetic_diff = np.linalg.norm(np.array(b.dna) - data[0])
            if genetic_diff <= tribe_dist:
                possible_tribes.append([tribe_id, genetic_diff])

        if possible_tribes:
            arr = np.array(possible_tribes)
            winner_idx = np.argmin(arr[:, 1])
            winning_tribe = int(arr[winner_idx, 0])
            tribes[winning_tribe][0] = ((tribes[winning_tribe][0] * tribes[winning_tribe][1]) + b.dna) / (tribes[winning_tribe][1] + 1)
            tribes[winning_tribe][1] += 1
            b.tribe = winning_tribe
        else:
            tribes[tribe_count] = [b.dna, 1]
            b.tribe = tribe_count
            tribe_count += 1

    #add all new babies to the main pop list
    neebler_pop.extend(new_babies)


    # some neeblers die of old age/starvation
    for i in sorted(death_indicies, reverse=True):
        if tribes[neebler_pop[i].tribe][1] != 1:
            tribes[neebler_pop[i].tribe][0] = ( (tribes[neebler_pop[i].tribe][0] * tribes[neebler_pop[i].tribe][1]) - neebler_pop[i].dna ) / (tribes[neebler_pop[i].tribe][1] - 1)
        tribes[neebler_pop[i].tribe][1] -= 1
        neebler_pop.pop(i)

    tribes = {t: data for t, data in tribes.items() if data[1] > 0}


    total_neeblers = len(neebler_pop)
    if total_neeblers <= 0:
        break


new_plant_count = int(growth_rate * len(plant_pop) * (1 - (len(plant_pop) / carrying_capacity)))
plant_pop.extend(Plant(random.random() * X_MAX, random.random() * Y_MAX) for snack in range(new_plant_count))

#plot
update_graphics(neebler_pop, plant_pop, (year + 1), year_end=True)

plt.pause(pause*0.1)


# print a report of the status of the last year
print()
print("The expiremint lasted " + str(year + 1) + " years")
print("Year " + str(year + 2) + ":")
print() 

print(str(len(plant_pop)) + " total plants")
print(str(total_neeblers) + " total creatures")
print()


# Keep the final plot window open
plt.ioff()
plt.show()