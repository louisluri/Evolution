"""Simulates natural selection in the fictional Neebler population."""
import matplotlib.pyplot as plt
import random
import numpy as np


def getwinner(indicies, probabilitys):
   """Takes in a list of things to chose from and an equal sized list of probabilitys
   it will normalize the probabilitys and then return one of the items in the indicies list"""

   total_score = np.sum(probabilitys)

   probs = probabilitys / total_score

   return np.random.choice(indicies, size=1, p=probs)[0]

def correct_direction(delta, max):
   """takes in a potential change in x or y and adjusts and returns the change to take the shortest path recognizing that you can go around the globe"""
   
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


class Neebler:
   def __init__(self, size, xcoord, ycoord, age=0):
      self.x = xcoord
      self.y = ycoord
      self.size = size
      self.gender = random.randint(0,1)  # 0=female 1=male
      self.age = age
      self.food = 0
      self.offspring = False
      self.hidden = False
      self.freeze = 0

class Plant:
   def __init__(self, x, y):
      self.x = x
      self.y = y

class Offspring:
   def __init__(self, mom_size, dad_size):
      self.momsize = mom_size
      self.dadsize = dad_size


# hyperparams
X_MAX = 140
Y_MAX = X_MAX # boundries of our fictional world

# eye ball offsets 
start_offset = 12
x_offset = 0.048 * (np.sqrt(X_MAX)/10)
y_offset = 0.033 * (np.sqrt(X_MAX)/10)
eye_scale = 7
pupil_scale = 55

# neebler size increments on the scatter
start_size = 4    # neeblers of size 0 have size start*increment on the plot
increment = 35 / (X_MAX/100)

# pause time
pause = 0.1 # step pause is pause * 0.1

max_age = 20 # max life span
min_reproduction_age = 1
max_reproduction_age = max_age * 0.7

num_neeblers = 80 #starting pop size

carrying_capacity = 400   #plant foods carrying capacity and starting point
growth_rate = 1.3

step_size = 2  # how far do the neeblers walk per step
interaction_distance = 2 # how far away can they interact with a food/neebler
sight_distance = 10 # how far will they see a predator/prey/food
born_distance = 10 # how far away can a baby be born from their mother (random.random() * born_distance) for x,y
freeze_steps = 2 # steps it takes to interact with something

goal_weight = 1.5 # how much goals like eating/ mating affect motion
fear_weight = 1.0 # how much fear of predators affect motion

mate_step = 1 # how many sizes away to mate (will break if this is >1)
pred_step = 1 # how many sizes below to be able to eat

mutation_chance = 0.10  #chance that a newborn has a trait thats diffrent to their parents

reproduce_food = {
0: 2, 1: 2, 2: 2, 
3: 2, 4: 2, 5: 2, 
6: 2, 7: 2, 8: 2
} # how many food must have been ate to reproduce 2 also garuntees survival so they will not eat more

neebler_meat = {
0: 1, 1: 1, 2: 1, 
3: 1, 4: 2, 5: 2, 
6: 2, 7: 2, 8: 2
} # how much food is rewarded for eating a neebler

#edge (size: chance)
eat_chance = {
0: 1, 1: 0.92, 2: 0.84, 
3: 0.76, 4: 0.68, 5: 0.6, 
6: 0.52, 7: 0.44, 8: 0.36
}

not_eaten_chance = 0.35 # chance that no one eats the plant (plants "resistance")

hunt_chance = {
0: 0.36, 1: 0.44, 2: 0.52, 
3: 0.6, 4: 0.68, 5: 0.76, 
6: 0.84, 7: 0.92, 8: 1
}  # chance that they catch the prey or they win over others to get the same prey

stealth_chance = {
0: 0.45, 1: 0.4, 2: 0.35, 
3: 0.3, 4: 0.25, 5: 0.2, 
6: 0.15, 7: 0.1, 8: 0.05
} # chance that a predator fails to eat the neebler

neebler_reserve = {
0: 5, 1: 3, 2: 0, 
3: 0, 4: 0, 5: 0, 
6: 0, 7: 0, 8: 0
} # number of this neebler that can go undetected by the predators

reserve = {
0: 0.50, 1: 0.53, 2: 0.56, 
3: 0.59, 4: 0.62, 5: 0.65, 
6: 0.68, 7: 0.71, 8: 0.74
} # % of the foods carrying capacity that MUST be respected by this size

#Labels and colors for graphing
COLORS = ['indigo', '#8A2BE2', 'b', 'c', 'g', 'y', 'orange', 'r', 'darkred']
abreviated_labels = ['XXS', 'XS', 'S', 'MS', 'M', 'ML', 'L', 'XL', 'XXL']
sizes_rev = [8, 7, 6, 5, 4, 3, 2, 1, 0]


#get starting neebler pop
neebler_pop = [Neebler(size=random.choice(sizes_rev), xcoord=random.random() * X_MAX, ycoord=random.random() * Y_MAX, age=random.randint(0,max_age)) for neebler in range(num_neeblers)]

sizes = np.array([neebler.size for neebler in neebler_pop])


#enable interactive mode
plt.ion()
fig, (ax_scatter, ax_bar) = plt.subplots(1, 2, figsize=(16, 7.5))

#start the population distribution bar chart
ax_bar.set_xlabel("Size", fontsize=12)
ax_bar.set_xlabel(f"Total Agents: {len(neebler_pop)}", fontsize=12)

#start the neebler position plot
ax_neeb = ax_scatter.scatter([neebler.x for neebler in neebler_pop], [neebler.y for neebler in neebler_pop],
                        s=(sizes + start_size) * increment, c=[COLORS[size] for size in sizes])

#plot fun little eyes for the neebs
ax_eye_L = ax_scatter.scatter([neebler.x - (x_offset * (sizes[i] + start_offset)) for i, neebler in enumerate(neebler_pop)], [neebler.y + (y_offset * (sizes[i] + start_offset)) for i, neebler in enumerate(neebler_pop)],
                               s=((sizes + start_size) * increment) / eye_scale, c='white', edgecolors='k', linewidths=0.2, zorder=2)
ax_eye_R = ax_scatter.scatter([neebler.x + (x_offset * (sizes[i] + start_offset)) for i, neebler in enumerate(neebler_pop)], [neebler.y + (y_offset * (sizes[i] + start_offset)) for i, neebler in enumerate(neebler_pop)],
                               s=((sizes + start_size) * increment) / eye_scale, c='white', edgecolors='k', linewidths=0.2, zorder=2)
ax_pupil_L = ax_scatter.scatter([neebler.x - (x_offset * (sizes[i] + start_offset)) for i, neebler in enumerate(neebler_pop)], [neebler.y + (y_offset * (sizes[i] + start_offset)) for i, neebler in enumerate(neebler_pop)],
                                 s=((sizes + start_size) * increment) / pupil_scale, c='black', zorder=3)
ax_pupil_R = ax_scatter.scatter([neebler.x + (x_offset * (sizes[i] + start_offset)) for i, neebler in enumerate(neebler_pop)], [neebler.y + (y_offset * (sizes[i] + start_offset)) for i, neebler in enumerate(neebler_pop)],
                                 s=((sizes + start_size) * increment) / pupil_scale, c='black', zorder=3)

ax_scatter.set_xlim(0, X_MAX)
ax_scatter.set_ylim(0, Y_MAX)
ax_scatter.set_title("Neebler Movement Simulation")
ax_scatter.grid(True, linestyle='--', color='gray', alpha=0.6)

#Initialize food
plant_pop = [Plant(random.randint(0, X_MAX), random.randint(0, Y_MAX)) for snack in range(carrying_capacity)]
ax_food = ax_scatter.scatter([], [], color='darkgreen', marker='s',alpha=0.4,label='Plant Resource', zorder=0)

plt.tight_layout() # Ensures titles and labels don't overlap
plt.draw()


for year in range(250):
   ax_scatter.set_xlabel(f"Total Plants: {len(plant_pop)}", fontsize=12)
   plt.pause(pause)

   # start each round with new food grown
   new_plant_count = int(growth_rate * len(plant_pop) * (1 - (len(plant_pop) / carrying_capacity)))
   plant_pop.extend(Plant(random.randint(0, X_MAX), random.randint(0, Y_MAX)) for snack in range(new_plant_count))
   foodx = [snack.x for snack in plant_pop]
   foody = [snack.y for snack in plant_pop]
   ax_food.set_offsets(np.c_[foodx, foody])
   start_year_plants = len(plant_pop)

   # sizes and colors for plotting
   sizes = np.array([neebler.size for neebler in neebler_pop])
   colors = [COLORS[size] for size in sizes]

   ax_bar.clear()  # Clear the bar chart for the new frame

   # update population distribution data
   size_data = np.bincount(sizes, minlength=9)

   # Draw the bar chart with the new order
   ax_bar.bar(abreviated_labels, size_data, color=COLORS)

   ax_bar.set_ylim(0, 70)
   
   # Re-set labels (which were also cleared)
   ax_bar.set_title(f"Population at Year {year + 1}")

   x_coords = np.array([neebler.x for neebler in neebler_pop])
   y_coords = np.array([neebler.y for neebler in neebler_pop])
   ax_neeb.set_offsets(np.c_[x_coords, y_coords])
   ax_neeb.set_sizes((sizes + start_size) * increment)
   ax_neeb.set_facecolors(colors)

   ax_eye_L.set_offsets(np.c_[x_coords - (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
   ax_eye_R.set_offsets(np.c_[x_coords + (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
   ax_pupil_L.set_offsets(np.c_[x_coords - (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
   ax_pupil_R.set_offsets(np.c_[x_coords + (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
   ax_eye_L.set_sizes(((sizes + start_size) * increment) / eye_scale)
   ax_eye_R.set_sizes(((sizes + start_size) * increment) / eye_scale)
   ax_pupil_L.set_sizes(((sizes + start_size) * increment) / pupil_scale)
   ax_pupil_R.set_sizes(((sizes + start_size) * increment) / pupil_scale)

   ax_scatter.set_xlabel(f"Total Plants: {len(plant_pop)}", fontsize=12)
   ax_bar.set_xlabel(f"Total Neeblers: {len(neebler_pop)}", fontsize=12)
   plt.pause(pause)


   #decide which neeblers will be fully safe from predators this round
   hidden = np.zeros((9,))
   for neebler in reversed(neebler_pop):
      neebler.hidden = False
      if hidden[neebler.size] < neebler_reserve[neebler.size]:
         neebler.hidden = True
         hidden[neebler.size] += 1

   #create a base of random directions to start the next round
   theta = np.random.uniform(0, 2 * np.pi, size=len(neebler_pop))


   # each year consists of some number of time steps for neeblers to find food and mate
   for time_step in range(25):

      #initialize the step size array as some may step less to get to their goals
      speeds = np.full(len(neebler_pop), step_size, dtype=np.float64)

      # moving with purpose
      for i, neebler in enumerate(neebler_pop):

         if neebler.freeze <= 0:
            goals = False #signifies if the neebler has any goals this step that it can achive through walking a direction
            fears = False #signifies if the neebler has any fears this step that it can avoid through walking a direction

            hungry = False #signifies if the neebler is hungry
            horny = False #signifies if the neebler is ready to mate

            deltax = 0 #initializes a dx and dy to change with its goals
            deltay = 0


            #neeblers that are hungry go towards food/biggest nearby prey
            closest_prey = False
            closest_plant = False
            if neebler.food < reproduce_food[neebler.size]:
               closest_prey_distance = X_MAX * 100
               current_prey_size = 0
               hungry = True
               
            # neeblers that are ready to mate go towards a potential mate
            closest_mate = False
            if neebler.food >= reproduce_food[neebler.size] and not neebler.offspring and min_reproduction_age <= neebler.age <= max_reproduction_age:
               closest_mate_distance = X_MAX * 100
               possible_sizes = [neebler.size - mate_step, neebler.size, neebler.size + mate_step]
               horny = True

            #figure out what predators are close and run away
            close_predators_dx = []
            close_predators_dy = []


            #loop through each other neebler once to see if there is any pull on the subjects direction
            for i2, neebler2 in enumerate(neebler_pop):
               deltax_min = correct_direction(neebler2.x - neebler.x, X_MAX)
               deltay_min = correct_direction(neebler2.y - neebler.y, Y_MAX)
               current_distance = np.sqrt((deltax_min)**2 + (deltay_min)**2)


               #check if the neebler is a potential mate
               if horny:
                  if (neebler2.gender != neebler.gender and not neebler2.offspring and
                  min_reproduction_age <= neebler2.age <= max_reproduction_age and neebler2.size in possible_sizes and
                     neebler2.food >= reproduce_food[neebler2.size] and current_distance <= closest_mate_distance):
                  
                     closest_mate_distance = current_distance
                     closest_mate = i2


               #each other interaction needs to be in range of sight
               if sight_distance >= current_distance:

                  #check if the neebler is a potential prey
                  if hungry:
                     if (neebler2.size + pred_step <= neebler.size and not neebler2.hidden and neebler2.size >= current_prey_size):
                        if ((current_prey_size == neebler2.size and current_distance < closest_prey_distance) or (current_prey_size < neebler2.size)):
                           closest_prey_distance = current_distance
                           current_prey_size = neebler2.size
                           closest_prey = i2

                  #check if the neebler is a potential predator
                  if neebler2.size >= neebler.size + pred_step and neebler2.food < reproduce_food[neebler2.size]:

                     close_predators_dx.append(deltax_min)
                     close_predators_dy.append(deltay_min)


            # check if any prey was found, if not check for plant food and update dx/dy
            if hungry:
               if closest_prey is not False:
                  deltax = correct_direction(neebler_pop[closest_prey].x - neebler.x, X_MAX)
                  deltay = correct_direction(neebler_pop[closest_prey].y - neebler.y, Y_MAX)
                  goal_dist = np.sqrt((deltax)**2 + (deltay)**2)
                  goals = True
               else:
                  for s, snack in enumerate(plant_pop):
                     deltax_min = correct_direction(neebler.x - snack.x, X_MAX)
                     deltay_min = correct_direction(neebler.y - snack.y, Y_MAX)
                     current_distance = np.sqrt((deltax_min)**2 + (deltay_min)**2)

                     if sight_distance >= current_distance and current_distance < closest_prey_distance:
                        closest_prey_distance = current_distance
                        closest_plant = s
                  
                  if closest_plant is not False:
                     deltax = correct_direction(plant_pop[closest_plant].x - neebler.x, X_MAX)
                     deltay = correct_direction(plant_pop[closest_plant].y - neebler.y, Y_MAX)
                     goal_dist = np.sqrt((deltax)**2 + (deltay)**2)
                     goals = True

            # check if any potential mates were detected and go towards them, overrides food direction as mating is more important to keep the pop going,
            # also rn if they ate enough to mate they will garunteed live
            if horny:
               if closest_mate is not False:
                  deltax = correct_direction(neebler_pop[closest_mate].x - neebler.x, X_MAX)
                  deltay = correct_direction(neebler_pop[closest_mate].y - neebler.y, Y_MAX)
                  goal_dist = np.sqrt((deltax)**2 + (deltay)**2)
                  goals = True

            # lastly check if any predators were found nearby, 
            # it will change path slightly based on the flee vector
            if close_predators_dx and close_predators_dy:
               flee_x, flee_y = 0, 0
               for index in range(len(close_predators_dx)):
                  pred_dist = np.sqrt((close_predators_dx[index])**2 + (close_predators_dy[index])**2)
                  weight = 1 / (pred_dist**2 + 0.001)

                  flee_x -= close_predators_dx[index] * weight
                  flee_y -= close_predators_dy[index] * weight

               deltax, deltay = normalize(deltax, deltay)
               flee_x, flee_y = normalize(flee_x, flee_y)

               deltax = (deltax * goal_weight) + (flee_x * fear_weight)
               deltay = (deltay * goal_weight) + (flee_y * fear_weight)
               fears = True


            # goals wouldve been flipped to true at any point that the neeblers dx/dy were updated to fulfill a goal,
            # if no goal the neeb will keep the same direction and turn a slight, random ammount
            if goals and fears:
               theta[i] = np.atan2(deltay, deltax)
            elif fears:
               theta[i] = np.atan2(deltay, deltax)
            elif goals:
               theta[i] = np.atan2(deltay, deltax)
               speeds[i] = min([goal_dist, step_size])
            else:
               if random.random() < 0.5:
                  theta[i] += random.random()
               else:
                  theta[i] -= random.random()


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

            if (distance <= interaction_distance and neebler.freeze <= 0 and neebler.food < reproduce_food[neebler.size] and
               ((len(plant_pop) - len(dead_plants))/ start_year_plants) > reserve[neebler.size]):
               
               # bigger neeblers dont get the plant food as often
               gets_ate = getwinner([0,1], [not_eaten_chance * (1 / eat_chance[neebler.size]**2), eat_chance[neebler.size]])
               if gets_ate == 1:
                  nearby_neebs_i.append(i)
                  nearby_neebs_p.append(eat_chance[neebler.size])

         if nearby_neebs_i:
            winning_neebler = getwinner(nearby_neebs_i, nearby_neebs_p)
            if winning_neebler != -1:
               neebler_pop[winning_neebler].food += 1
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
         predatory_neebs_p = []  # probs/ hunt score

         # if they are ready to mate the loop will look for mates
         horny = False
         horny_neebs_i = []  # list of possible mates
         if (neebler.gender == 0 and neebler.food >= reproduce_food[neebler.size] and not neebler.offspring and
            min_reproduction_age <= neebler.age <= max_reproduction_age and i not in death_indicies):
            
            horny = True
            possible_sizes = [neebler.size - mate_step, neebler.size, neebler.size + mate_step]


         #loop through each other neebler once
         for i2, neebler2 in enumerate(neebler_pop):
            if interaction_distance >= np.sqrt((correct_direction(neebler.x - neebler2.x, X_MAX))**2 + (correct_direction(neebler.y - neebler2.y, Y_MAX))**2):

               # check if any nearby predators eat the subject neeb
               if not neebler.hidden:
                  if (neebler2.size >= neebler.size + pred_step and neebler2.food < reproduce_food[neebler.size] and i2 not in death_indicies and
                     neebler2.freeze <= 0 and i not in death_indicies):
                     
                     # stealth is more effective when the size dif is bigger
                     size_dif = neebler2.size - neebler.size

                     kill_chance = hunt_chance[neebler2.size] * (1 - min(1, stealth_chance[neebler.size] * ((size_dif/6)**2 + 1)))

                     if random.random() <= kill_chance:
                        predatory_neebs_i.append(i2)
                        predatory_neebs_p.append(hunt_chance[neebler2.size])


               #check if any nearby mates mate with the subject neeb
               if horny:
                  if (neebler2.gender == 1 and neebler2.food >= reproduce_food[neebler2.size] and min_reproduction_age <= neebler2.age <= max_reproduction_age
                     and neebler2.freeze <= 0 and neebler2.size in possible_sizes):
                     
                     horny_neebs_i.append(i2)

         # if any predators were added to the list then one will win and our subject neeb is eaten
         if predatory_neebs_i:
            winning_neebler = getwinner(predatory_neebs_i, predatory_neebs_p)
            neebler_pop[winning_neebler].food += neebler_meat[neebler.size]
            neebler_pop[winning_neebler].freeze = freeze_steps
            death_indicies.append(i)
            continue

         # if any mates were added to the list then one will be chosen and they will mate
         if horny_neebs_i:
            winning_neebler = random.choice(horny_neebs_i)
            neebler.offspring = Offspring(neebler.size, neebler_pop[winning_neebler].size)
            neebler.freeze = freeze_steps
            neebler_pop[winning_neebler].freeze = freeze_steps


      for i in sorted(death_indicies, reverse=True):
         neebler_pop.pop(i)

      theta = np.delete(theta, death_indicies)


      #update scatterplot
      sizes = np.array([neebler.size for neebler in neebler_pop])
      colors = [COLORS[size] for size in sizes]

      foodx = [snack.x for snack in plant_pop]
      foody = [snack.y for snack in plant_pop]
      ax_food.set_offsets(np.c_[foodx, foody])

      x_coords = np.array([neebler.x for neebler in neebler_pop])
      y_coords = np.array([neebler.y for neebler in neebler_pop])
      ax_neeb.set_offsets(np.c_[x_coords, y_coords])
      ax_neeb.set_sizes((sizes + start_size) * increment)
      ax_neeb.set_facecolors(colors)

      ax_eye_L.set_offsets(np.c_[x_coords - (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
      ax_eye_R.set_offsets(np.c_[x_coords + (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
      ax_pupil_L.set_offsets(np.c_[x_coords - (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
      ax_pupil_R.set_offsets(np.c_[x_coords + (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
      ax_eye_L.set_sizes(((sizes + start_size) * increment) / eye_scale)
      ax_eye_R.set_sizes(((sizes + start_size) * increment) / eye_scale)
      ax_pupil_L.set_sizes(((sizes + start_size) * increment) / pupil_scale)
      ax_pupil_R.set_sizes(((sizes + start_size) * increment) / pupil_scale)

      plt.pause(pause*0.1)


   #update neebler pop before and after reproduction
   ax_bar.set_xlabel(f"Total Neeblers: {len(neebler_pop)}", fontsize=12)


   death_indicies = []
   # end of year loop, check for starved/ old neebs
   for i, neebler in enumerate(neebler_pop):
      # age each neebler by one year
      neebler.age += 1
      if neebler.age >= max_age:
         death_indicies.append(i)
      elif neebler.food == 0:
         death_indicies.append(i)
      elif neebler.food == 1:
         if random.randint(1,10) < neebler.size:
            death_indicies.append(i)
      neebler.food = 0

   # new neeblers are born
   for neebler in neebler_pop:
      if neebler.offspring == False:
         continue
      else:
         large_size = max(neebler.offspring.momsize, neebler.offspring.dadsize)
         small_size = min(neebler.offspring.momsize, neebler.offspring.dadsize)
         if random.random() <= mutation_chance:
            if small_size == 0:
               rand = 0.01
            elif large_size == 8:
               rand = 1
            else:
               rand = random.random()

            if rand <= 0.5:
               neebler_pop.append(Neebler(large_size+1, (neebler.x + (random.random() * born_distance)) % X_MAX, (neebler.y + (random.random() * born_distance)) % Y_MAX))
            else:
               neebler_pop.append(Neebler(small_size-1, (neebler.x + (random.random() * born_distance)) % X_MAX, (neebler.y + (random.random() * born_distance)) % Y_MAX))
         else:
            rand = random.randint(1,2)
            if rand == 1:
               neebler_pop.append(Neebler(large_size, (neebler.x + (random.random() * born_distance)) % X_MAX, (neebler.y + (random.random() * born_distance)) % Y_MAX))
            else:
               neebler_pop.append(Neebler(small_size, (neebler.x + (random.random() * born_distance)) % X_MAX, (neebler.y + (random.random() * born_distance)) % Y_MAX))
         neebler.offspring = False


   # some neeblers die of old age/starvation
   for i in sorted(death_indicies, reverse=True):
      neebler_pop.pop(i)


   sexes = np.array([neebler.gender for neebler in neebler_pop], dtype=np.int64)
   sex_data = np.bincount(sexes, minlength=2)
   total_neeblers = len(neebler_pop)
   if total_neeblers <= 1 or sex_data[0] == 0 or sex_data[1] == 0:
      break


#collect final data
sizes = np.array([neebler.size for neebler in neebler_pop], dtype=np.int64)
size_data = np.bincount(sizes, minlength=9)
sexes = np.array([neebler.gender for neebler in neebler_pop], dtype=np.int64)
sex_data = np.bincount(sexes, minlength=2)


#update final plot
ax_bar.clear()
ax_bar.bar(abreviated_labels, size_data, color=COLORS)
ax_bar.set_ylim(0, 70)

ax_scatter.set_xlabel(f"Total Plants: {len(plant_pop)}", fontsize=12)
ax_bar.set_title(f"Population at Year {year + 1}")
ax_bar.set_xlabel(f"Total Agents: {len(neebler_pop)}", fontsize=12)
colors = [COLORS[size] for size in sizes]

foodx = [snack.x for snack in plant_pop]
foody = [snack.y for snack in plant_pop]
ax_food.set_offsets(np.c_[foodx, foody])

x_coords = np.array([neebler.x for neebler in neebler_pop])
y_coords = np.array([neebler.y for neebler in neebler_pop])
ax_neeb.set_offsets(np.c_[x_coords, y_coords])
ax_neeb.set_sizes((sizes + start_size) * increment)
ax_neeb.set_facecolors(colors)

ax_eye_L.set_offsets(np.c_[x_coords - (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
ax_eye_R.set_offsets(np.c_[x_coords + (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
ax_pupil_L.set_offsets(np.c_[x_coords - (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
ax_pupil_R.set_offsets(np.c_[x_coords + (x_offset * (sizes + start_offset)), y_coords + (y_offset * (sizes + start_offset))])
ax_eye_L.set_sizes(((sizes + start_size) * increment) / eye_scale)
ax_eye_R.set_sizes(((sizes + start_size) * increment) / eye_scale)
ax_pupil_L.set_sizes(((sizes + start_size) * increment) / pupil_scale)
ax_pupil_R.set_sizes(((sizes + start_size) * increment) / pupil_scale)

plt.pause(pause*0.1)


# print a report of the status of the last year
print("The expiremint lasted " + str(year + 1) + " years")
print("Year " + str(year + 2) + ":")
print() 
for sex in range(2):
   print(f"{str(sex_data[sex])} {'female' if sex == 0 else 'male'} neeblers left") 
print() 
for size in sizes_rev:
   print(str(size_data[size]) + " " + abreviated_labels[size] + " neeblers") 
print()
print(str(len(plant_pop)) + " total plants")
print(str(total_neeblers) + " total creatures")
print()


# Keep the final plot window open
plt.ioff()
plt.show()