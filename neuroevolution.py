"""Simulates natural selection in the fictional Neebler population."""
import os
os.environ["OMP_NUM_THREADS"] = "4" # only use the 4 performance cores
os.environ["OPENBLAS_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["VECLIB_MAXIMUM_THREADS"] = "4"
os.environ["NUMEXPR_NUM_THREADS"] = "4"

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import numpy as np
import random

def on_press(event):
    if event.key == ' ':
        global is_paused
        is_paused = not is_paused
    if event.key == 'n':
        global step_pause, year_pause, speed
        if speed == 1:
            step_pause = 0.06
            year_pause = 1
            speed = 0
        elif speed == 0:
            step_pause = 0.0000001
            year_pause = 0.0000001
            speed = 1

def get_colors(brains):

    brains = np.atleast_3d(brains)

    move_tendencies = np.sum(brains, axis=2)

    output_size = move_tendencies.shape[1]

    split_1 = output_size // 3
    split_2 = 2 * (output_size // 3)

    # Group into RGB buckets
    r = np.sum(move_tendencies[:, :split_1], axis=1)
    g = np.sum(move_tendencies[:, split_1:split_2], axis=1)
    b = np.sum(move_tendencies[:, split_2:], axis=1)

    #Stack into (Pop, 3)
    rgb = np.stack([r, g, b], axis=1)

    rgb = 1 / (1 + np.exp(-rgb * 1.5))

    return rgb

def update_graphics(neebler_x, neebler_y, neebler_brain1, gen, survived=False):
    
    colors = get_colors(neebler_brain1)


    x_coords = np.array([x for x in neebler_x])
    y_coords = np.array([y for y in neebler_y])
    ax_neeb.set_offsets(np.c_[x_coords, y_coords])
    ax_neeb.set_facecolor(colors)

    ax_map.set_xlabel(f"Generation {gen} | Pop: {len(neebler_x)}", fontsize=12)

    if survived:
        pop_history['surv'].append(len(neebler_x))
        pop_history['gen'].append(gen)
        plot_lines['surv'].set_data(pop_history['gen'], pop_history['surv'])

        ax_pop.relim()
        ax_pop.autoscale_view()


def get_shifted_map(grid, shift_y, shift_x):
    # Roll (Shift) the array
    # Note: np.roll wraps edges to the other side (Toroid), which we don't want
    shifted = np.roll(grid, shift=(shift_y, shift_x), axis=(0, 1))
    
    # Fix the "Wrap-around" (Make them walls instead)
    if shift_y > 0: # We shifted DOWN, so Top is garbage
        shifted[:shift_y, :] = 1
    elif shift_y < 0: # We shifted UP, so Bottom is garbage
        shifted[shift_y:, :] = 1
        
    if shift_x > 0: # We shifted RIGHT, so Left is garbage
        shifted[:, :shift_x] = 1
    elif shift_x < 0: # We shifted LEFT, so Right is garbage
        shifted[:, shift_x:] = 1
        
    return shifted

def softmax(z):
    # We subtract max(z) for numerical stability (prevents overflow)
    exp_z = np.exp(z - np.max(z))
    return exp_z / exp_z.sum()

def mutate_population(brains, mutation_rate=0.05, strength=0.1):
    # Vectorized Mutation: Mutates the entire population array at once!
    mask = np.random.random(brains.shape) < mutation_rate
    noise = np.random.normal(0, strength, brains.shape)
    brains[mask] += noise[mask]
    return brains


is_paused = True
speed = 1

debug = False

pop_history = {'gen': [], 'surv': []}  # for line plotting
plot_lines = {}

# hyperparams
X_MAX = 128
Y_MAX = X_MAX # boundries of our fictional world

step_pause = 0.0000001
year_pause = 0.0000001

num_years = 10000
num_steps = 200

num_neeblers = 2000   # starting pop

#get starting neebler pop
neebler_x = np.array([random.randint(0, X_MAX) for n in range(num_neeblers)])
neebler_y = np.array([random.randint(0, Y_MAX) for n in range(num_neeblers)])
neebler_brain1 = np.array([np.random.normal(0, 1, size=(200, 10)) for n in range(num_neeblers)])
neebler_brain2 = np.array([np.random.normal(0, 1, size=(5, 200)) for n in range(num_neeblers)])
#neebler_brain3 = np.array([np.random.normal(0, 1, size=(5, 200)) for n in range(num_neeblers)])


#enable interactive mode
plt.ion()
fig1 = plt.figure(figsize=(16, 7.53))

fig1.canvas.mpl_connect('key_press_event', on_press)

gs1 = gridspec.GridSpec(4, 4, figure=fig1, width_ratios=[1, 1, 0.8, 0.8])
ax_map = fig1.add_subplot(gs1[:, :2], facecolor="#dbdace99")
ax_map.set_xlabel(f"Generation {0} | Pop: {len(neebler_x)}", fontsize=12)
ax_map.set_xlim(0-1, X_MAX+1)
ax_map.set_ylim(0-1, Y_MAX+1)
ax_map.set_xticks([])
ax_map.set_yticks([])

"""zones = [
        patches.Rectangle((20.5, 20.5), 20, 25, ec='green', fc='none', ls='--'),
        patches.Rectangle((82.5, 20.5), 25, 20, ec='green', fc='none', ls='--'),
        patches.Rectangle((87.5, 82.5), 20, 25, ec='green', fc='none', ls='--'),
        patches.Rectangle((20.5, 87.5), 25, 20, ec='green', fc='none', ls='--')
    ]"""
zones = [patches.Rectangle((41.5, 41.5), 45, 45, ec='green', fc='none', ls='--')]
for z in zones: ax_map.add_patch(z)

for spine in ax_map.spines.values():
    spine.set_linewidth(2.5)
    spine.set_edgecolor('black')

ax_neeb = ax_map.scatter([], [], s=15, edgecolors='k', linewidths=0.2)

ax_pop = fig1.add_subplot(gs1[:, 2:])
ax_pop.grid(True)
ax_pop.set_xlabel('Gen')
ax_pop.set_ylabel('Survived')
plot_lines['surv'], = ax_pop.plot([], [], linestyle='-', label='Survived', color='g')

# all brain data for plotting
colors = get_colors(neebler_brain1)
ax_neeb.set_facecolor(colors)

plt.tight_layout()

plt.draw()

directions = [(1, -1), (1, 0), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1)] # the sensor directions
move_dir = np.array([[1, 0], [0, -1], [0, 0], [0, 1], [-1, 0]])  # possible move directions

for gen in range(num_years):
    plt.pause(year_pause)

    update_graphics(neebler_x, neebler_y, neebler_brain1, gen)

    plt.pause(year_pause)

    while is_paused:
        plt.pause(0.1)

    for time_step in range(num_steps):


        padded_positions = np.ones((Y_MAX+3, X_MAX+3))
        positions = np.zeros((Y_MAX+1, X_MAX+1)) 
        positions[neebler_y, neebler_x] = 1
        padded_positions[1:-1, 1:-1] = positions

        sensor_maps = []

        for dy, dx in directions:
            # We want to bring the neighbor TO us.
            # If neighbor is North (-1), we shift the world South (+1) to overlap.
            # So we pass (-dy, -dx) to the shift function.
            layer = get_shifted_map(positions, -dy, -dx)
            sensor_maps.append(layer)

        # Convert to a 3D array: Shape (8, 128, 128)
        world_sensors = np.stack(sensor_maps)


        # get sensory input
        s_data = world_sensors[:, neebler_y, neebler_x].T
        l_data = np.stack([(neebler_x/X_MAX)-0.5, (neebler_y/Y_MAX)-0.5], axis=1)
        input_data = np.concatenate([s_data, l_data], axis=1)[..., np.newaxis]

        if debug: 
            rand_neeb_idx = random.randint(0, num_neeblers)
            print(f"Neebler {rand_neeb_idx} Inputs")
            print()
            print(f"x: {neebler_x[rand_neeb_idx]} | y: {neebler_y[rand_neeb_idx]}")
            print()
            print(f"Sensors: ")
            print(f"{input_data[rand_neeb_idx][0]}, {input_data[rand_neeb_idx][1]}, {input_data[rand_neeb_idx][2]}")
            print(f"{input_data[rand_neeb_idx][3]}, ____, {input_data[rand_neeb_idx][4]}")
            print(f"{input_data[rand_neeb_idx][5]}, {input_data[rand_neeb_idx][6]}, {input_data[rand_neeb_idx][7]}")
            print(f"{input_data[rand_neeb_idx][8]}, {input_data[rand_neeb_idx][9]}")
            print()
            print()
            #print(f"Brain1: ")
            #print(f"{neebler_brain1[rand_neeb_idx]}")
            #print()
            #print(f"Brain2: ")
            #print(f"{neebler_brain2[rand_neeb_idx]}")
            #print()


        # Forward pass
        scores = neebler_brain1 @ input_data
        scores = np.maximum(0, scores)
        scores = neebler_brain2 @ scores
        if debug: 
            #print(f"Logits: ")
            #print(f"{scores[rand_neeb_idx]}")
            #print()
            #print()
            is_paused = True
            while is_paused:
                plt.pause(0.1)
        moves_idx = np.argmax(scores.squeeze(), axis=1)
        

        chosen_moves = move_dir[moves_idx]
        dys, dxs = chosen_moves[:, 0], chosen_moves[:, 1]
        tys = np.clip(neebler_y + dys, 0, Y_MAX)
        txs = np.clip(neebler_x + dxs, 0, X_MAX)

        is_move_safe = padded_positions[tys+1, txs+1] == 0

        # Handle "Collision Conflicts" (Two neeblers trying to move to the SAME empty spot)
        # We pack coordinates into a single integer to check uniqueness easily
        target_indices = tys * (X_MAX + 1) + txs

        # Find unique targets; fcfs
        _, winner_indices = np.unique(target_indices, return_index=True)

        # Create a boolean mask for the whole population (initially all False)
        is_winner = np.zeros(len(neebler_x), dtype=bool)

        # Set the "Winners" to True
        is_winner[winner_indices] = True

        # Combine safety and uniqueness
        valid_moves_mask = is_move_safe & is_winner & (moves_idx != 2) # 2 is 'stay'

        # Apply the moves instantly using the mask
        # Only update the Neeblers who have a valid, safe, unique move
        final_y = np.where(valid_moves_mask, tys, neebler_y)
        final_x = np.where(valid_moves_mask, txs, neebler_x)

        # Update the master arrays
        neebler_y = final_y
        neebler_x = final_x
                
        update_graphics(neebler_x, neebler_y, neebler_brain1, gen)

        if debug: 
            print(f"Chosen_move: {chosen_moves[rand_neeb_idx]}")
            print()
            print(f"dx, dy: {(dxs[rand_neeb_idx], dys[rand_neeb_idx])}")
            print()
            print(f"tx, ty: {(txs[rand_neeb_idx], tys[rand_neeb_idx])}")
            print()
            print(f"x: {neebler_x[rand_neeb_idx]} | y: {neebler_y[rand_neeb_idx]}")
            print()
            print()
            print("--------------")
        
        plt.pause(step_pause)

    """survivor_mask = (
        ((21 <= neebler_x) & (neebler_x <= 40) & (21 <= neebler_y) & (neebler_y <= 45)) |
        ((83 <= neebler_x) & (neebler_x <= 107) & (21 <= neebler_y) & (neebler_y <= 40)) |
        ((88 <= neebler_x) & (neebler_x <= 107) & (83 <= neebler_y) & (neebler_y <= 107)) |
        ((21 <= neebler_x) & (neebler_x <= 45) & (88 <= neebler_y) & (neebler_y <= 107))
    )"""
    survivor_mask = (
        ((42 <= neebler_x) & (neebler_x <= 86) & (42 <= neebler_y) & (neebler_y <= 86))
    )

    neebler_x = neebler_x[survivor_mask]
    neebler_y = neebler_y[survivor_mask]
    neebler_brain1 = neebler_brain1[survivor_mask]
    neebler_brain2 = neebler_brain2[survivor_mask]

    update_graphics(neebler_x, neebler_y, neebler_brain1, gen, survived=True)

    while is_paused:
        plt.pause(0.1)
    
    if len(neebler_brain1) == 0:
        print("Extinction!")
        break

    indices = np.arange(len(neebler_x))
    np.random.shuffle(indices)

    num_survivors = len(neebler_brain1)
    parent_indices = np.array([indices[i % num_survivors] for i in range(num_neeblers)])

    new_brain1 = neebler_brain1[parent_indices]
    new_brain2 = neebler_brain2[parent_indices]


    neebler_brain1 = mutate_population(new_brain1)
    neebler_brain2 = mutate_population(new_brain2)
    neebler_x = np.random.randint(0, X_MAX, num_neeblers)
    neebler_y = np.random.randint(0, Y_MAX, num_neeblers)




# Keep the final plot window open
plt.ioff()
plt.show()