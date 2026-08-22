"""Simulates natural selection in the fictional Neebler population."""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import random
import numpy as np


def getwinner(indicies, probabilitys):
   """Takes in a list of things to chose from and an equal sized list of probabilitys
   it will normalize the probabilitys and then return one of the items in the indicies list"""

   probabilitys = np.maximum(probabilitys, 0)

   total_score = np.sum(probabilitys)

   probs = probabilitys / total_score

   return np.random.choice(indicies, size=1, p=probs)[0]

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

def get_win_prob(subject, opponent, is_attacking=False):
   """The probability of one neebler winning a fight aginst another, "is_attacking" refers to the subject neeb"""

   if is_attacking:
      diff = (subject.dna[0] + 1) - opponent.dna[0]
   else:
      diff = subject.dna[0] - opponent.dna[0]

   return 1 / (1 + np.exp(-0.8 * diff))

def wants_to_fight(subject, opponent, current_time, max_time, is_attacking=False):
   """Decides if the Neebler engages based on risk tolerance.
   if the time before the reproduce/starvation check is less then they will take more risks
   Bravery 0.0 (Coward): Needs 99% win chance to fight.
   Bravery 1.0 (Rambo):  Will fight even with low win chance (e.g. 20%)."""

   win_prob = get_win_prob(subject, opponent, is_attacking=is_attacking)
   if subject.metabolism != subject.food:
      reward = min(1, opponent.meat * subject.meat_bonus / (subject.metabolism - subject.food)) * min(1, (current_time * 2 /max_time))
   else:
      reward = 0
   # Scale bravery so even crazy ones don't fight impossible odds (0% chance)
   # Risk Threshold: The minimum win chance required to attack.
   # High bravery lowers the threshold.
   risk_threshold = 1.0 - (0.6 * (subject.dna[4] + 5) / 15) * ((((subject.dna[5] + 5) / 15) * 0.3) + (reward * 0.7))
   return win_prob >= risk_threshold

def update_graphics(neebler_pop, plant_pop, year, hist=False):
   """
   neebler_pop: List of Neebler objects
   plant_pop:   List of Plant objects
   year:        Current year (int)
   hist:        Update Histograms too?
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

   # Create Empty Color Array (N rows, 3 columns for RGB)
   colors = np.zeros((len(neebler_pop), 3))
   
   # RED Channel: Influenced by Size (idx0) and Diet/Carnivore (idx5)
   # Big meat eaters will tend toward Red/Magenta.Small herbivores toward Cyan.
   colors[:, 0] = (dna_matrix[:, 0] + dna_matrix[:, 5])**2 / 200

   # GREEN Channel: Influenced by Speed (idx1) and Stealth (idx3)
   # Fast, sneaky neeblers will tend toward Green/Yellow.
   colors[:, 1] = (dna_matrix[:, 1] + dna_matrix[:, 3])**2 / 200

   # BLUE Channel: Influenced by Perception (idx2) and Bravery (idx4)
   # Perceptive, brave neeblers will tend toward Blue/Cyan.
   colors[:, 2] = (dna_matrix[:, 2] + dna_matrix[:, 4])**2 / 200

   colors = (colors - 0.5) * 1.5 + 0.5  # Extra Contrast
   colors = np.clip(colors, 0, 1) # Ensure valid RGB range

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
   ax_pupil_L.set_sizes(((dna_matrix[:, 0] + start_size) * increment * (((dna_matrix[:, 2] + 5)**2 / 100))) / pupil_scale)
   ax_pupil_R.set_sizes(((dna_matrix[:, 0] + start_size) * increment * (((dna_matrix[:, 2] + 5)**2 / 100))) / pupil_scale)

   sex_data = np.bincount(np.array([n.gender for n in neebler_pop], dtype=np.int64), minlength=2)

   ax_map.set_xlabel(f"Year {year} | Pop: {len(neebler_pop)} | F: {sex_data[0]} | M: {sex_data[1]} | Plants: {len(plant_pop)}", fontsize=12)

   if hist:
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
         ax.hist(dna_matrix[:, col], bins=25, range=(min(0, min(dna_matrix[:, col])), max(10, max(dna_matrix[:, col]))), color=color, alpha=0.7, edgecolor='black')
         ax.set_title(name, fontsize=12, pad=3)
         ax.set_xlim(min(0, min(dna_matrix[:, col])), max(10, max(dna_matrix[:, col])))
         ax.set_yticks([])
         ax.grid(True, linestyle='--', color='gray', alpha=0.6)

class Neebler:
   def __init__(self, mom_xcoord=None, mom_ycoord=None, parents_dna=None, age=0):
      if mom_xcoord is None and mom_ycoord is None and parents_dna is None:
         self.x = X_MAX * random.random()
         self.y = Y_MAX * random.random()
         self.dna = [np.random.rand() * 10, # idx0, size
                     np.random.rand() * 10, # idx1, speed
                     np.random.rand() * 10, # idx2, perception
                     np.random.rand() * 10, # idx3, stealth
                     np.random.rand() * 10, # idx4, fear/greed
                     np.random.rand() * 10] # idx5, herb/carn
      elif mom_xcoord is not None and mom_ycoord is not None and parents_dna is not None:
         self.x = (mom_xcoord + (((random.random() * 2) - 1) * born_distance)) % Y_MAX
         self.y = (mom_ycoord + (((random.random() * 2) - 1) * born_distance)) % Y_MAX
         self.dna = [random.gauss(np.mean(parents_dna[:, 0]), mutation_rate), 
                     random.gauss(np.mean(parents_dna[:, 1]), mutation_rate), 
                     random.gauss(np.mean(parents_dna[:, 2]), mutation_rate),
                     random.gauss(np.mean(parents_dna[:, 3]), mutation_rate), 
                     random.gauss(np.mean(parents_dna[:, 4]), mutation_rate), 
                     random.gauss(np.mean(parents_dna[:, 5]), mutation_rate)]
      else:
         raise ValueError("You tried to create a neebler with inadequate info from the parent")

      self.metabolism = 1.0 + ((self.dna[0] / 10)**2 * 4) + (((self.dna[1] / 10)**2 * 6) * ((13 - self.dna[3]) / 10)) + ((self.dna[2] / 10)**2 * 2) # need this much food to garunteed live and to procreate
      self.sight = ((3 + self.dna[2]) / 13) * 25                                 # how far away can this neebler see
      self.speed = ((self.dna[1]) + 10) * (2/10) * ((10 - self.dna[3]) / 10)     # speed is altered down by high stealth
      self.eat_chance = ((10 - self.dna[5]) + 0.01)**2                           # their chance to eat a plant that can be weighed aginst other potential neeblers nearby
      self.plant_bonus = ((8 - self.dna[5]) / 5)**2                              # multiplies with the plant to get the ammount of food rewarded, "digestion"
      self.meat_bonus = (self.dna[5] / 5)**2                                     # multiplies with the meat to get the ammount of food rewarded, "digestion"
      self.plant_reserve = 0.55 + (self.dna[5] / 50)                              # what % of the plants must be preserved by this neeb
      self.stealth = (12 - self.dna[3]) / 10                                     # this will multiply/divide the surrounding neeblers sight
      self.meat = (self.dna[0]) + 1                                              # how much nourishment is offered to a pred that catches this neeb

      self.gender = random.randint(0,1)  # 0=female 1=male
      self.age = age                     # how old is this neeb?
      self.food = 0                      # the food it has ate this year
      self.offspring = False             # this will hold the dads dna list when pregnant and help dictate the traits of the baby
      self.freeze = 0                    # this dictates how many steps the neebler is frozen in place for
      self.want_plants = False           # checks if a predator wahts plants since they have no better options, resets every step

class Plant:
   def __init__(self, xcoord, ycoord):
      self.x = xcoord
      self.y = ycoord


# hyperparams
X_MAX = 100
Y_MAX = X_MAX # boundries of our fictional world

# eye ball offsets 
start_offset = 12
x_offset = 0.06 * (np.sqrt(X_MAX)/10)
y_offset = 0.04 * (np.sqrt(X_MAX)/10)
eye_scale = 7
pupil_scale = 50

# neebler size increments on the scatter
start_size = 3    # neeblers of size 0 have size start*increment on the plot
increment = 50 / (X_MAX/100)

# pause time
pause = 0.5              # step pause is pause * 0.1

max_age = 20             # max life span
min_reproduction_age = 1
max_reproduction_age = max_age * 0.7

num_neeblers = 80       # starting pop size

carrying_capacity = int(400 * (X_MAX / 100)) # plant foods carrying capacity and starting point
growth_rate = 1.6

interaction_distance = 2 # how far away can they interact with a food/neebler
born_distance = 5        # how far away can a baby be born from their mother (random.random() * born_distance) for x,y
freeze_steps = 2         # steps it takes to interact with something
steps_per_year = 30

mutation_rate = 0.6         # std dev for the baby creation
twins_chance = 0.3          # Chance of twins, gets modifies by a neeblers size  * ((20 - neebler.dna[0]) / 10)
genetic_compatibility = 10   # Max distance allowed between DNA vectors to mate
cannibalism_threshold = 2   # Min distance of dna vectors to attack another neeb

neebler_reserve = 0.7       # % of prey neebs(< mean size at start of year) that cant be eaten
want_plant_threshhold = 0.2  # % of a neeblers remaining metabolism that has to be satisfied by a plant for a neebler to eat plants


#get starting neebler pop
neebler_pop = [Neebler(age=random.randint(0,max_age)) for neebler in range(num_neeblers)]

#Initialize food
plant_pop = [Plant(random.random() * X_MAX, random.random() * Y_MAX) for snack in range(carrying_capacity)]


#enable interactive mode
plt.ion()
fig = plt.figure(figsize=(16, 7.53))

gs = gridspec.GridSpec(3, 4, figure=fig, width_ratios=[1, 1, 0.8, 0.8])

ax_map = fig.add_subplot(gs[:, :2])
ax_map.set_title("Neebler World")
ax_map.set_xlim(0, X_MAX)
ax_map.set_ylim(0, Y_MAX)
ax_map.grid(True, linestyle='--', color='gray', alpha=0.6)

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
ax_size    = fig.add_subplot(gs[0, 2])
ax_speed   = fig.add_subplot(gs[0, 3])# Row 0

ax_percep  = fig.add_subplot(gs[1, 2])
ax_stealth = fig.add_subplot(gs[1, 3])# Row 1

ax_bravery = fig.add_subplot(gs[2, 2])
ax_diet    = fig.add_subplot(gs[2, 3])# Row 2

plt.tight_layout(rect=[0, 0.03, 1, 1]) # Ensures titles and labels don't overlap

plt.draw()


for year in range(250):
   plt.pause(pause)

   # start each round with new food grown
   new_plant_count = int(growth_rate * len(plant_pop) * (1 - (len(plant_pop) / carrying_capacity)))
   plant_pop.extend(Plant(random.random() * X_MAX, random.random() * Y_MAX) for snack in range(new_plant_count))
   start_year_plants = len(plant_pop)

   #plot
   update_graphics(neebler_pop, plant_pop, year, hist=True)

   plt.pause(pause)


   #create a base of random directions to start the next round
   theta = np.random.uniform(0, 2 * np.pi, size=len(neebler_pop))

   # for upholding the neebler reserve
   sizes = np.array([n.dna[0] for n in neebler_pop])
   prey_threshhold = np.percentile(sizes, 50)
   current_prey_count = np.sum(sizes < prey_threshhold)
   start_prey_count = current_prey_count


   # each year consists of some number of time steps for neeblers to find food and mate
   for time_step in range(steps_per_year):

      #initialize the step size array as some may step less to get to their goals
      speeds = np.array([neebler.speed for neebler in neebler_pop])

      # moving with purpose
      for i, neebler in enumerate(neebler_pop):

         if neebler.freeze <= 0:
            goals = False #signifies if the neebler has any goals this step that it can achive through walking a direction
            fears = False #signifies if the neebler has any fears this step that it can avoid through walking a direction

            hungry = False #signifies if the neebler is hungry
            horny = False #signifies if the neebler is ready to mate

            neebler.want_plants = False

            deltax, deltay = np.cos(theta[i]), np.sin(theta[i]) #initializes a dx and dy to change with its goals
            goal_x, goal_y = 0, 0


            #neeblers that are hungry go towards food/biggest nearby prey
            best_seen_prey_dx, best_seen_prey_dy = False, False
            closest_plant_dx, closest_plant_dy = False, False
            prey_dx, prey_dy = [], []   # if the plant food is not adequate enough, they will instinctually be steered in the direction of prey, even if not in range
            searching_for_prey = False  # if the neebler is not satisfied by plants and doesnt see a prey
            current_prey_value = 0  # how much food is rewarded for eating

            if neebler.food < neebler.metabolism:
               closest_prey_distance = X_MAX * 100
               best_seen_prey_distance = X_MAX * 100
               hungry = True
               

            # neeblers that are ready to mate go towards a potential mate
            closest_mate_dx, closest_mate_dy = False, False
            if neebler.food >= neebler.metabolism and not neebler.offspring and min_reproduction_age <= neebler.age <= max_reproduction_age:
               closest_mate_distance = X_MAX * 100
               horny = True


            #figure out what predators are close and run away
            close_predators_dx, close_predators_dy = [], []


            # there is also a vector pulling them towards geneticly similar neebs even when not horny
            herding = False
            if neebler.food >= neebler.metabolism:
               close_tribe_dx, close_tribe_dy = [], []
               close_hostile_dx, close_hostile_dy = [], []


            #loop through each other neebler once to see if there is any pull on the subjects direction
            for neebler2 in neebler_pop:
               deltax_min = correct_direction(neebler2.x - neebler.x, X_MAX)
               deltay_min = correct_direction(neebler2.y - neebler.y, Y_MAX)
               current_distance = np.sqrt((deltax_min)**2 + (deltay_min)**2)
               genetic_diff = np.linalg.norm(np.array(neebler.dna) - np.array(neebler2.dna))
               wants_fight = wants_to_fight(neebler, neebler2, time_step, steps_per_year, is_attacking=True)


               #check if the neebler is a potential mate
               if horny:
                  if (neebler2.gender != neebler.gender and not neebler2.offspring and min_reproduction_age <= neebler2.age <= max_reproduction_age
                       and neebler2.food >= neebler2.metabolism and current_distance <= closest_mate_distance and genetic_diff <= genetic_compatibility):
                  
                     closest_mate_distance = current_distance
                     closest_mate_dx, closest_mate_dy = deltax_min, deltay_min


               # even if not horny try to stay near tribe
               if neebler.food >= neebler.metabolism and cannibalism_threshold >= genetic_diff:

                  close_tribe_dx.append(deltax_min)
                  close_tribe_dy.append(deltay_min)

               # even if not horny try to stay away from hostiles
               if neebler.food >= neebler.metabolism and cannibalism_threshold < genetic_diff:

                  close_hostile_dx.append(deltax_min)
                  close_hostile_dy.append(deltay_min)


               # check for all possible prey on map (if neebler doesnt want plants and doesnt see prey, it will instinctually gravitate)
               if (hungry and wants_fight and ((neebler2.dna[0] >= prey_threshhold) or (neebler2.dna[0] < prey_threshhold and (current_prey_count - 1) / start_prey_count > neebler_reserve)) and
                  cannibalism_threshold < genetic_diff):

                  prey_dx.append(deltax_min)
                  prey_dy.append(deltay_min)


               #each other movement choice needs to be in range of sight
               if neebler.sight * neebler2.stealth >= current_distance:


                  #check if the neebler is a potential prey
                  if (hungry and wants_fight and ((neebler2.dna[0] >= prey_threshhold) or (neebler2.dna[0] < prey_threshhold and (current_prey_count - 1) / start_prey_count > neebler_reserve)) and 
                      cannibalism_threshold < genetic_diff and neebler2.meat * neebler.meat_bonus >= current_prey_value and
                      ((current_prey_value == neebler2.meat * neebler.meat_bonus and current_distance < best_seen_prey_distance) or 
                      (current_prey_value < neebler2.meat * neebler.meat_bonus))):
                           
                     best_seen_prey_distance = current_distance
                     current_prey_value = neebler2.meat * neebler.meat_bonus
                     best_seen_prey_dx, best_seen_prey_dy = deltax_min, deltay_min
                     continue


                  #check if the neebler is a potential predator to run from
                  if (cannibalism_threshold < genetic_diff and not wants_to_fight(neebler, neebler2, time_step, steps_per_year, is_attacking=False) and
                     wants_to_fight(neebler2, neebler, time_step, steps_per_year, is_attacking=True) and neebler2.food < neebler2.metabolism):

                     close_predators_dx.append(deltax_min)
                     close_predators_dy.append(deltay_min)


            # check if any prey was found, if plant food yeilds more nourishment prioritize that
            if hungry:
               if (((neebler.plant_bonus >= current_prey_value and neebler.plant_bonus >= (neebler.metabolism - neebler.food) * want_plant_threshhold) or
                     not prey_dx) and (len(plant_pop)/ start_year_plants) > neebler.plant_reserve):
                  neebler.want_plants = True
                  for s, snack in enumerate(plant_pop):
                     deltax_min = correct_direction(snack.x - neebler.x, X_MAX)
                     deltay_min = correct_direction(snack.y - neebler.y, Y_MAX)
                     current_distance = np.sqrt((deltax_min)**2 + (deltay_min)**2)

                     if neebler.sight >= current_distance and best_seen_prey_distance > current_distance:
                        best_seen_prey_distance = current_distance
                        closest_plant_dx, closest_plant_dy = deltax_min, deltay_min
                  
               if closest_plant_dx:
                  goal_x = closest_plant_dx
                  goal_y = closest_plant_dy
                  goal_dist = np.sqrt((goal_x)**2 + (goal_y)**2)
                  goals = True
               elif best_seen_prey_dx:
                  goal_x = best_seen_prey_dx
                  goal_y = best_seen_prey_dy
                  goal_dist = np.sqrt((goal_x)**2 + (goal_y)**2)
                  goals = True
               elif not neebler.want_plants and prey_dx and not best_seen_prey_dx:
                  searching_for_prey = True


            # check if any potential mates were detected and go towards them,
            # also rn if they ate enough to mate they will garunteed live
            if horny:
               if closest_mate_dx:
                  goal_x = closest_mate_dx
                  goal_y = closest_mate_dy
                  goal_dist = np.sqrt((goal_x)**2 + (goal_y)**2)
                  if goal_dist <= speeds[i]:
                     goal_dist /= 1.5
                  goals = True

            # if they are on the search for prey but dont see any yet, find the best direction to travel
            prey_x, prey_y = 0, 0
            if searching_for_prey and hungry:
               for index in range(len(prey_dx)):
                  prey_dist = np.sqrt((prey_dx[index])**2 + (prey_dy[index])**2)
                  weight = 1 / (prey_dist**3 + 0.1)

                  prey_x += prey_dx[index] * weight
                  prey_y += prey_dy[index] * weight

               prey_x, prey_y = normalize(prey_x, prey_y)

            # lastly check if any predators were found nearby, 
            # it will change path slightly based on the flee vector
            flee_x, flee_y = 0, 0
            if close_predators_dx:
               fears = True
               for index in range(len(close_predators_dx)):
                  pred_dist = np.sqrt((close_predators_dx[index])**2 + (close_predators_dy[index])**2)
                  weight = 1 / (pred_dist**2 + 0.1)

                  flee_x -= close_predators_dx[index] * weight
                  flee_y -= close_predators_dy[index] * weight

               flee_x, flee_y = normalize(flee_x, flee_y)

            # pull them towards their tribe if they have eaten enough and dont have a mating vector
            herding_x, herding_y = 0, 0
            if closest_mate_dx is False and neebler.food >= neebler.metabolism:
               tribe_x, tribe_y = 0, 0
               hostile_x, hostile_y = 0, 0
               near_tribe = False
               near_hostile = False
               for index in range(len(close_tribe_dx)):
                  tribe_dist = np.sqrt((close_tribe_dx[index])**2 + (close_tribe_dy[index])**2)
                  weight = 1 / (tribe_dist + 0.1)

                  # Personal Space
                  if tribe_dist < 5: # If too close
                     # Push away hard!
                     tribe_x -= close_tribe_dx[index] * weight
                     tribe_y -= close_tribe_dy[index] * weight
                  else:
                     # Otherwise pull together
                     tribe_x += close_tribe_dx[index] * weight
                     tribe_y += close_tribe_dy[index] * weight

                  tribe_x, tribe_y = normalize(tribe_x, tribe_y)

                  if tribe_dist <= neebler.sight:
                     near_tribe = True

               if near_tribe:
                  for index in range(len(close_hostile_dx)):
                     hostile_dist = np.sqrt((close_hostile_dx[index])**2 + (close_hostile_dy[index])**2)
                     if hostile_dist <= neebler.sight * 2:
                        near_hostile = True
                     weight = 1 / (hostile_dist**2 + 0.1)

                     hostile_x -= close_hostile_dx[index] * weight
                     hostile_y -= close_hostile_dy[index] * weight
                     hostile_x, hostile_y = normalize(hostile_x, hostile_y)

               herding = True

               herding_x = (tribe_x) + (hostile_x)
               herding_y = (tribe_y) + (hostile_y)
               herding_x, herding_y = normalize(herding_x, herding_y)

            if goals or fears or herding:
               deltax, deltay = 0, 0
            else:
               deltax, deltay = normalize(deltax, deltay)

            goal_x, goal_y = normalize(goal_x, goal_y)

            #if year > 3 and time_step > 10 and neebler.dna[0] >= prey_threshhold:
            #   print(f"""({neebler.x:.3f}, {neebler.y:.3f})
            #   delta:({deltax:.3f}, {deltay:.3f})
            #   goal:({goal_x:.3f}, {goal_y:.3f})
            #   prey:({prey_x:.3f}, {prey_y:.3f})
            #   flee:({flee_x:.3f}, {flee_y:.3f})
            #   herd:({herding_x:.3f}, {herding_y:.3f})
            #   tribe:({tribe_x:.3f}, {tribe_y:.3f})
            #   host:({hostile_x:.3f}, {hostile_y:.3f})
            #   -
            #   goals:{goals}, fears:{fears}, herding:{herding}, searchingforprey:{searching_for_prey}
            #   horny:{horny}, hungry:{hungry}
            #   food_eaten:{neebler.food:.3f}, met:{neebler.metabolism:.3f}
            #   plant_reserve:{neebler.plant_reserve:.3f}
            #   -
            #   size:{neebler.dna[0]:.3f}, speed:{neebler.dna[1]:.3f}, perception::{neebler.dna[2]:.3f}
            #   stealth:{neebler.dna[3]:.3f}, greed::{neebler.dna[4]:.3f}, diet:{neebler.dna[5]:.3f}
            #   """)

            deltax += (goal_x * 2) + (prey_x * 0.35) + (flee_x) + (herding_x * 1.5)
            deltay += (goal_y * 2) + (prey_y * 0.35) + (flee_y) + (herding_y * 1.5)

            #if year > 3 and time_step > 10 and neebler.dna[0] >= prey_threshhold:
            #   print(f"""dxdy({deltax:.3f}, {deltay:.3f})
            #         
            #         """)


            # goals wouldve been flipped to true at any point that the neeblers dx/dy were updated to fulfill a goal,
            # if no goal the neeb will keep the same direction and turn a slight, random ammount
            if deltax == 0 and deltay == 0:
               theta[i] += random.random() - 0.5
            elif herding and near_tribe and not near_hostile:
               speeds[i] /= 2
               theta[i] = np.atan2(deltay, deltax)
            elif goals:
               theta[i] = np.atan2(deltay, deltax)
               speeds[i] = min([goal_dist, neebler.speed])
            else:
               theta[i] = np.atan2(deltay, deltax)

      #if year > 3 and time_step > 20:
      #   print(f"% prey remaining:{current_prey_count/start_prey_count:.3f} preythresh:{prey_threshhold:.3f}")
      #   print(f"% plants remaining:{len(plant_pop)/start_year_plants:.3f}")
      #   input("next step?")

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
         nearby_neebs_p = []    #list of probs

         for i, neebler in enumerate(neebler_pop):
            distance = np.sqrt((correct_direction(neebler.x - snack.x, X_MAX))**2 + (correct_direction(neebler.y - snack.y, Y_MAX))**2)

            if (distance <= interaction_distance and neebler.freeze <= 0 and neebler.food < neebler.metabolism and
                 ((len(plant_pop) - len(dead_plants))/ start_year_plants) > neebler.plant_reserve):
            
                  nearby_neebs_i.append(i)
                  nearby_neebs_p.append(neebler.eat_chance)

         if nearby_neebs_i:
            winning_neebler = getwinner(nearby_neebs_i, nearby_neebs_p)
            neebler_pop[winning_neebler].food += neebler_pop[winning_neebler].plant_bonus
            neebler_pop[winning_neebler].freeze = freeze_steps
            dead_plants.append(s)

      #plants that got ate get removed from plant pop
      for i in sorted(dead_plants, reverse=True):
         plant_pop.pop(i)

         
      # each nearby neebler has a chance to be eat them or mate
      death_indicies = []
      for i, neebler in enumerate(neebler_pop):

         # the loop will always look for possible predators
         predatory_neebs_i = []  # indicies

         # if they are ready to mate the loop will look for mates
         horny = False
         horny_neebs_i = []  # list of possible mates
         if (neebler.gender == 0 and neebler.food >= neebler.metabolism and not neebler.offspring and
            min_reproduction_age <= neebler.age <= max_reproduction_age and i not in death_indicies):
            
            horny = True


         #loop through each other neebler once
         for i2, neebler2 in enumerate(neebler_pop):

            if i in death_indicies:
               break

            if interaction_distance >= np.sqrt((correct_direction(neebler.x - neebler2.x, X_MAX))**2 + (correct_direction(neebler.y - neebler2.y, Y_MAX))**2):
               genetic_diff = np.linalg.norm(np.array(neebler.dna) - np.array(neebler2.dna))

               # check if any nearby predators eat the subject neeb
               if ((neebler.dna[0] >= prey_threshhold) or (neebler.dna[0] < prey_threshhold and (current_prey_count - 1) / start_prey_count > neebler_reserve)):
                  if (cannibalism_threshold < genetic_diff and wants_to_fight(neebler2, neebler, time_step, steps_per_year, is_attacking=True) and neebler2.food < neebler2.metabolism and
                     i2 not in death_indicies and neebler2.freeze <= 0 and i not in death_indicies):

                     if ((neebler.food < neebler.metabolism and wants_to_fight(neebler, neebler2, time_step, steps_per_year, is_attacking=True)) or
                           (neebler.food >= neebler.metabolism and wants_to_fight(neebler, neebler2, time_step, steps_per_year, is_attacking=False))):
                        win_chance = get_win_prob(neebler2, neebler, is_attacking=False)
                     else:
                        win_chance = get_win_prob(neebler2, neebler, is_attacking=True)

                     if random.random() < win_chance:
                        neebler2.food += neebler.meat * neebler2.meat_bonus
                        neebler2.freeze = freeze_steps
                        death_indicies.append(i)
                        if neebler.dna[0] < prey_threshhold:
                           current_prey_count -= 1
                        break
                     else:
                        neebler.food += neebler2.meat * neebler.meat_bonus
                        neebler.freeze = freeze_steps
                        death_indicies.append(i2)
                        if neebler2.dna[0] < prey_threshhold:
                           current_prey_count -= 1

               #check if any nearby mates mate with the subject neeb
               if horny:
                  if (i2 not in death_indicies and neebler2.gender == 1 and neebler2.food >= neebler2.metabolism and 
                      min_reproduction_age <= neebler2.age <= max_reproduction_age and neebler2.freeze <= 0 and
                      genetic_diff <= genetic_compatibility):
                     
                     horny_neebs_i.append(i2)


         # if any mates were added to the list then one will be chosen and they will mate
         if horny_neebs_i:
            winning_neebler = random.choice(horny_neebs_i)
            neebler.offspring = neebler_pop[winning_neebler].dna
            neebler.freeze = freeze_steps
            neebler_pop[winning_neebler].freeze = freeze_steps


      for i in sorted(death_indicies, reverse=True):
         neebler_pop.pop(i)

      theta = np.delete(theta, death_indicies)


      #plot
      update_graphics(neebler_pop, plant_pop, year, hist=False)

      plt.pause(pause*0.1)


   death_indicies = []
   # end of year loop, check for starved/ old neebs
   for i, neebler in enumerate(neebler_pop):
      # age each neebler by one year
      neebler.age += 1
      if neebler.age >= max_age:
         death_indicies.append(i)
      elif neebler.food < neebler.metabolism:
         survival_chance = neebler.food / neebler.metabolism
         if random.random() > survival_chance:
            death_indicies.append(i)
      neebler.food = 0

   # new neeblers are born
   new_babies = []
   for neebler in neebler_pop:
      if neebler.offspring == False:
         continue
      else:
         if random.random() < twins_chance * ((20 - (neebler.dna[0] * 2)) / 10):
            new_babies.append(Neebler(neebler.x, neebler.y, np.array([neebler.dna, neebler.offspring])))
            new_babies.append(Neebler(neebler.x, neebler.y, np.array([neebler.dna, neebler.offspring])))
         else:
            new_babies.append(Neebler(neebler.x, neebler.y, np.array([neebler.dna, neebler.offspring])))
         neebler.offspring = False
   
   #add all new babies to the main pop list
   neebler_pop.extend(new_babies)


   # some neeblers die of old age/starvation
   for i in sorted(death_indicies, reverse=True):
      neebler_pop.pop(i)


   sex_data = np.bincount(np.array([neebler.gender for neebler in neebler_pop], dtype=np.int64), minlength=2)
   total_neeblers = len(neebler_pop)
   if total_neeblers <= 1 or sex_data[0] == 0 or sex_data[1] == 0:
      break


#plot
update_graphics(neebler_pop, plant_pop, (year + 1), hist=True)

plt.pause(pause*0.1)


# print a report of the status of the last year
print()
print("The expiremint lasted " + str(year + 1) + " years")
print("Year " + str(year + 2) + ":")
print() 

for sex in range(2):
   print(f"{str(sex_data[sex])} {'female' if sex == 0 else 'male'} neeblers left") 
print() 

print(str(len(plant_pop)) + " total plants")
print(str(total_neeblers) + " total creatures")
print()


# Keep the final plot window open
plt.ioff()
plt.show()