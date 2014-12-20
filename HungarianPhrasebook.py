#coding: utf-8
# Hungarian Phrasebook, <https://www.youtube.com/watch?v=G6D1YI-41ao>
# Use with Pythonista

# The MIT License
# 
# Copyright Â© 2014 Mia Sinno Smith and Steven Thomas Smith
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import math, os, re, sound, time
from scene import *
import random
from itertools import cycle
from functools import partial

class HungarianPhrasebook (Scene):
	def setup(self):
		# This will be called before the first frame is drawn.
		# add bounds and size by hand if run from console
		if not hasattr(self,'bounds'):
			self.bounds = Rect(0, 0, 1024, 748)
		if not hasattr(self,'size'):
			self.size = Size(1024, 748)
		self.HP_init()
		
		# Set up the root layer and one other layer:
		self.root_layer = Layer(self.bounds)
		self.root_layer.background = Color(0.2,0.2,0.2)
		self.totcols = 2*self.ncols + 1		# user row + reveal + Pythonista row
		self.sepx = 5
		self.card_size = math.floor((self.size.w-(self.totcols+6)*self.sepx)/self.totcols)	# 96 if self.size.w > 700 else 48
		self.width = (self.card_size + self.sepx) * self.totcols + 6*self.sepx		# xtra space between guess and Pythonista row
		self.height = self.size.h - (self.card_size + self.sepx)
		self.offset = Point((self.size.w - self.width)/2,self.height)
		
		self.deal_cards()
		
	def HP_init(self):
		# define Hungarian Phrasebook variables and functions
		self.ncols = 4
		self.ncolors = 7
		
		self.guesses = []
		self.pguesses = []
		self.hyps = ()
		self.phyps = ()
		self.rows = []
		self.prows = []
		self.prows_revealed = []
		self.guess_cards = []
		self.pcards_deal_flag = True
		emoji = self.emoji()
		
		self.ncolors = max(1,self.ncolors)
		self.ncolors = min(len(emoji),self.ncolors)
		
		# characters
		self.characters = []
		self.colors = []
		while len(self.characters) < self.ncolors:
			k = random.randint(0,len(emoji)-1)
			self.characters.append(emoji[k])
			self.colors.append(Color(random.random(), random.random(), random.random()))
			del emoji[k]
		
		# The game
		# colored and white pegs, standard sorting
		self.rpegs = {'R': 1, 'W': 2, '-': 3, ' ': 4}

		# define peg letters for hash table
		self.firstletter = 'A'
		self.chrpegs = dict((k,chr(ord(self.firstletter)+k-1)) for k in range(0,self.ncolors))

		# the result
		self.default_result = ['-'] * self.ncols

		# the truth
		self.truth = "".join([chr(random.randint(0,self.ncolors-1)+ord(self.firstletter)) for x in range(self.ncols)])
		# print 'Truth is ' + repr([self.characters[k] for k in self.codetocards(self.truth)])

		# guesses and results
		self.nhyp = []
		self.nhyp.append(self.ncolors**self.ncols)
		
	def emoji(self):
		# List of Pythonista emoji
		emoji = os.listdir(sys.path[0] + 'Textures');
		emoji = filter(lambda k: re.match('^[A-Z].+\.png',k) and
		               not re.match('^(ionicons|Typicons|PC_)',k),emoji);
		emoji = [k.replace(".png","") for k in emoji]
		cute_emoji = ['Ant','Baby_Chick_1','Baby_Chick_2','Baby_Chick_3','Bactrian_Camel','Bear_Face',
		              'Bird','Blowfish','Boar','Bug','Cat_Face_Crying','Cat_Face_Grinning',
		              'Cat_Face_Heart-Shaped_Eyes','Cat_Face_Kissing','Cat_Face_Pouting',
		              'Cat_Face_Smiling','Cat_Face_Weary','Cat_Face_With_Tears_Of_Joy',
		              'Cat_Face_With_Wry_Smile','Cat_Face','Chicken','Cow_Face','Dog_Face',
		              'Dolphin','Elephant','Fish','Frog_Face','Hamster_Face','Honeybee',
		              'Horse_Face','Horse','Koala','Lady_Beetle','Monkey_Face',
		              'Monkey_Hear-No-Evil','Monkey_See-No-Evil','Monkey_Speak-No-Evil',
		              'Monkey','Mouse_Face','Octopus','Panda_Face',
		              'Penguin','Pig_Face','Pig_Nose','Poodle','Rabbit_Face','Sheep',
		              'Snail','Snake','Spiral_Shell','Tiger_Face','Tropical_Fish','Turtle',
		              'Whale','Wolf_Face','Aubergine','Banana','Birthday_Cake','Bread',
		              'Candy','Cherries','Chestnut','Chocolate_Bar','Coffee','Cooked_Rice',
		              'Cookie','Cooking','Corn','Doughnut','Grapes','Green_Apple','Hamburger',
		              'Ice_Cream','Lollipop','Meat_On_Bone','Melon','Oden','Peach','Pineapple',
		              'Pot_Of_Food','Poultry_Leg','Red_Apple','Shaved_Ice','Shortcake',
		              'Slice_Of_Pizza','Soft_Ice_Cream','Spaghetti','Strawberry','Tangerine',
		              'Tomato','Watermelon','Alien_Monster','Artist_Palette','Balloon',
		              'Crown','Crystal_Ball','Gem_Stone','Honey_Pot','Jack-O-Lantern','Moyai',
		              'Musical_Keyboard','Package','Party_Popper','Pile_Of_Poo','Ribbon',
		              'Snowman_Without_Snow','Alien','Baby','Boy','Ghost','Girl','Guardsman',
		              'Man_And_Woman','Man','Older_Man','Older_Woman','Person_Blond',
		              'Police_Officer','Princess','Woman','Worker','Blossom','Bouquet',
		              'Cactus','Cherry_Blossom','Four_Leaf_Clover','Hibiscus','Maple_Leaf',
		              'Mushroom','Palm_Tree','Rose','Sunflower','Tulip','Smiling_1',
		              'Stuck-Out_Tongue_2','Card_Joker','Cloud','Cyclone','Fire','Heart',
		              'Moon_5','Recycling_Symbol','Skull','Speech_Balloon','Sun_1','Rocket']
		if True:
			return cute_emoji
		else:
			return emoji
	
	def advance_row(self):
		self.guesses.append(self.cardstocode(self.cards))
		self.rows.append(self.cards)
		if len(self.guesses) == 1:
			self.hyps = self.make_hypspace(self.guesses[-1])
		else:
			self.hyps = self.reduce_hypspace(self.hyps,self.guesses[-1])
		if self.height - (self.card_size + self.sepx) < 0:
			self.game_over()
			return
		self.deal_pcards()
		self.height -= (self.card_size + self.sepx)
		self.deal_cards()
	
	def deal_cards(self):
		self.cards = []
		for k in range(self.ncols):
			card = Layer(Rect(self.offset.x + k * (self.card_size + self.sepx),self.height,
			                  self.card_size, self.card_size))
			card.icyc = cycle(range(0,self.ncolors))
			for k in range(random.randint(1,self.ncolors)):
				card.idx = card.icyc.next()
			card.background = self.colors[card.idx]
			card.image = self.characters[card.idx]
			card.stroke = Color(0.6, 0.6, 0.6)
			card.stroke_weight = 4.0
			self.root_layer.add_layer(card)
			self.cards.append(card)
		guess_card = Layer(Rect(self.offset.x + self.ncols * (self.card_size + self.sepx)+2*self.sepx,
		                        self.height, self.card_size, self.card_size))
		guess_card.background = Color(0.95,0.95,0.95)
		guess_card.stroke = Color(1.0, 0.65, 1.0)
		guess_card.stroke_weight = 4.0
		guess_card.revealed = False
		self.root_layer.add_layer(guess_card)
		self.guess_cards.append(guess_card)
		self.font_size = 60 if self.size.w > 700 else 48
		guess_layer = TextLayer('?', 'GillSans', self.font_size)
		guess_layer.frame.center(guess_card.frame.x + guess_card.frame.w / 2,
		                         guess_card.frame.y + guess_card.frame.h / 2)
		guess_layer.tint = Color(1.0,0.0,1.0)
		self.root_layer.add_layer(guess_layer)
		self.guess_layer = guess_layer
		font_size = 24 if self.size.w > 700 else 12
		if len(self.guesses) == 0:
			# You
			self.youtext_layer = TextLayer(
			                               'You, {}^{} = {} words'.format(
			                                self.ncolors,self.ncols,self.ncolors**self.ncols),
			                                'Futura', font_size)
			self.youtext_layer.frame.center(self.offset.x 
			                        + (self.ncols * (self.card_size + self.sepx) - self.sepx)/2,
			                        self.height-1.2*font_size/2)
			self.root_layer.add_layer(self.youtext_layer)
			# Pythonista
			self.ptext_layer = TextLayer(
			                               'Pythonista, {}^{} = {} words'.format(
			                                self.ncolors,self.ncols,self.ncolors**self.ncols),
			                                'Futura', font_size)
			self.ptext_layer.frame.center(self.offset.x
			                        + (self.ncols+1) * (self.card_size + self.sepx) + 2*self.sepx
			                        + (self.ncols * (self.card_size + self.sepx) - self.sepx)/2,
			                        self.height + 0.608*self.card_size + self.sepx - 1.2*font_size/2)
			self.root_layer.add_layer(self.ptext_layer)
		else:
			# You
			plural = 's' if len(self.hyps) > 1 else ''
			youtext_layer = TextLayer(
			                          'You, {} word{}'.format(len(self.hyps),plural),
			                          'Futura', font_size)
			youtext_layer.frame.center(self.offset.x 
			                        + (self.ncols * (self.card_size + self.sepx) - self.sepx)/2,
			                        self.height-1.2*font_size/2)
			self.root_layer.remove_layer(self.youtext_layer)
			self.youtext_layer = youtext_layer
			self.root_layer.add_layer(self.youtext_layer)
			# Pythonista
			if not self.pcards_deal_flag: return
			plural = 's' if len(self.phyps) > 1 else ''
			ptext_layer = TextLayer(
			                          'Pythonista, {} word{}'.format(len(self.phyps),plural),
			                          'Futura', font_size)
			ptext_layer.frame.center(self.offset.x
			                        + (self.ncols+1) * (self.card_size + self.sepx) + 2*self.sepx
			                        + (self.ncols * (self.card_size + self.sepx) - self.sepx)/2,
			                        self.height + self.card_size + self.sepx - 1.2*font_size/2)
			self.root_layer.remove_layer(self.ptext_layer)
			self.ptext_layer = ptext_layer
			self.root_layer.add_layer(self.ptext_layer)
			if self.redandwhitepegs(self.pguesses[-1],self.truth) == 'R' * self.ncols:
				self.ptext_layer.tint = Color(0.8, 0.8, 1.0)
				self.pcards_deal_flag = False

	def deal_pcards(self):
		if not self.pcards_deal_flag: return
		self.pcards = []
		if len(self.pguesses) == 0:
			# First guess is random, then use it to create an initial (truncated) hypothesis space
			self.pguesses.append("".join([chr(random.randint(0,self.ncolors-1)+ord(self.firstletter))
			                               for x in range(self.ncols)]))
			self.phyps = self.make_hypspace(self.pguesses[0])
		else:
			self.pguesses.append(random.sample(self.phyps,1)[0])
			self.phyps = self.reduce_hypspace(self.phyps,self.pguesses[-1])
		pcards_nos = self.codetocards(self.pguesses[-1])
		for k in range(self.ncols):
			card = Layer(Rect(self.offset.x + (self.ncols+1+k) * (self.card_size + self.sepx)+6*self.sepx,
			                  self.height, self.card_size, self.card_size))
			card.idx = pcards_nos[k]
			if False:
				# only reveal python's guesses if asked
				card.background = self.colors[self.pcards[k]]
				card.image = self.characters[self.pcards[k]]
			else:
				card.background = Color(0.8,0.8,1.0)
			card.stroke = Color(0.3, 0.3, 0.6)
			card.stroke_weight = 4.0
			self.root_layer.add_layer(card)
			self.pcards.append(card)
		self.prows.append(self.pcards)
		self.prows_revealed.append(False)
		
	def game_win(self):
		font_size = 100 if self.size.w > 700 else 50
		text_layer = TextLayer('You Win!', 'Futura', font_size)
		text_layer.frame.center(self.bounds.center())
		overlay = Layer(self.bounds)
		overlay.background = Color(0, 0, 0, 0)
		overlay.add_layer(text_layer)
		self.add_layer(overlay)
		overlay.animate('background', Color(0.0, 0.2, 0.3, 0.7))
		text_layer.animate('scale_x', 1.3, 0.3, autoreverse=True)
		text_layer.animate('scale_y', 1.3, 0.3, autoreverse=True)
		self.root_layer.animate('scale_x', 0.0, delay=2.0,
						curve=curve_ease_back_in)
		self.root_layer.animate('scale_y', 0.0, delay=2.0,
						curve=curve_ease_back_in,
						completion=self.game_over)
		
	def game_over(self):
		sound.play_effect('Powerup_2')
		self.delay(0.5,self.setup)

	def redandwhitepegs(self,test,truth):
		res = list(self.default_result)
		for p in range(0,len(truth)):
				if test[p] == truth[p]:
					res[p] = 'R'
				elif test[p] in truth:
					res[p] = 'W'
		return "".join(sorted(res,key=lambda c: self.rpegs[c]))

	def cardstocode(self,cards):
		return "".join([chr(card.idx+ord(self.firstletter)) for card in cards])

	def codetocards(self,code):
		return [ord(c)-ord(self.firstletter) for c in list(code)]

	def draw_result(self,rpegs,rcenter):
		ns = int(math.ceil(sqrt(len(rpegs))))
		sl = int(math.ceil(2.0/(sqrt(5.0)+1.0)*self.card_size/ns))
		slx = sl + int(math.ceil((self.card_size - ns*sl)/(ns+2)))
		rcenter.x -= (ns * sl + (ns-1) * (slx-sl))/2
		rcenter.y += ((ns-2) * sl + (ns-1) * (slx-sl))/2
		for k in xrange(len(rpegs)):
			i, j = k / ns, k % ns
			if rpegs[k] in 'RW':
				rpeg = Layer(Rect(rcenter.x + j * slx,
				                  rcenter.y - i * slx,
				                  sl, sl))
				rpeg.background = Color(1.0, 0.0, 1.0) if rpegs[k] == 'R' else Color(1.0, 1.0, 1.0)
				self.root_layer.add_layer(rpeg)

	# possible outcomes -- reduce from ncols**ncolors using the first guess
	def make_hypspace(self,guess):
		hyps = set()
		result = self.redandwhitepegs(guess,self.truth)
		firstnn = [0] * self.ncols
		while firstnn[0] < self.ncolors:
			hyp = "".join([chr(x+ord(self.firstletter)) for x in firstnn])
			if result == self.redandwhitepegs(guess,hyp):
				hyps.add(hyp)
			firstnn[-1] += 1
			for d in range(1,self.ncols):
				if firstnn[-d] >= self.ncolors:
					firstnn[-d] = 0; firstnn[-d-1] += 1
		return hyps

	def reduce_hypspace(self,hyps,guess):
		newhyps = set()
		result = self.redandwhitepegs(guess,self.truth)
		for hyp in hyps:
			if result == self.redandwhitepegs(guess,hyp):
				newhyps.add(hyp)
		return newhyps

	def draw(self):
		# Update and draw our root layer. For a layer-based scene, this
		# is usually all you have to do in the draw method.
		background(0, 0, 0)
		self.root_layer.update(self.dt)
		self.root_layer.draw()
	
	def touch_began(self, touch):
		# Animate the layer to the location of the touch:
		#x, y = touch.location.x, touch.location.y
		#new_frame = Rect(x - 64, y - 64, 128, 128)
		#self.layer.animate('frame', new_frame, 1.0, curve=curve_bounce_out)
		# Animate the background color to a random color:
		for card in self.cards:
			if touch.location in card.frame:
				def reveal_card():
					card.idx = card.icyc.next()
					card.background = self.colors[card.idx]
					card.image = self.characters[card.idx]
					card.animate('scale_y', 1.0, 0.15)
				card.animate('scale_y', 0.0, 0.15,
				             completion=reveal_card)
				card.scale_x = 1.0
				card.animate('scale_x', 0.9, 0.15, autoreverse=True)
				sound.play_effect('Click_1')
				time.sleep(0.2)
				break
		guess_card = self.guess_cards[-1]
		if touch.location in guess_card.frame and not guess_card.revealed:
			def reveal_card():
					guess_card.background = Color(0.1, 0.1, 0.1)
					guess_card.stroke = Color(1.0, 0.2, 1.0)
					guess_card.revealed = True
					guess_card.animate('scale_y', 1.0, 0.15)
			guess_card.animate('scale_y', 0.0, 0.15,
			             completion=reveal_card)
			self.guess_layer.remove_layer()
			guess_card.scale_x = 1.0
			guess_card.animate('scale_x', 0.9, 0.15, autoreverse=True)
			sound.play_effect('8ve-slide-magic')
			result = self.redandwhitepegs(self.cardstocode(self.cards),self.truth)
			self.draw_result(result,guess_card.frame.center())
			if result == 'R' * self.ncols:
				self.game_win()
				return
			self.advance_row()
		self.pcards_reveal_flag = False
		for k in range(len(self.prows)):
			pcards = self.codetocards(self.pguesses[k])
			for l in range(len(self.prows[k])):
				if touch.location in self.prows[k][l].frame:
					self.pcards_reveal_flag = True
					break
			if self.pcards_reveal_flag: break
		if self.pcards_reveal_flag:
			cards = list(self.prows[k])
			if self.prows_revealed[k]: cards.reverse()
			if not self.prows_revealed[k]:
				def reveal_cards(card):
					card.background = self.colors[card.idx]
					card.image = self.characters[card.idx]
					card.animate('scale_y', 1.0, 0.15)
			else:
				def reveal_cards(card):
					card.background = Color(0.8,0.8,1.0)
					card.image = None
					card.animate('scale_y', 1.0, 0.15)
			for l in range(len(cards)):
				card = cards[l]
				card.animate('scale_y', 0.0, 0.15,l*0.05,
				             completion=partial(reveal_cards,card))
				card.scale_x = 1.0
				card.animate('scale_x', 0.9, 0.15, autoreverse=True)
			if not self.prows_revealed[k]:
				sound.play_effect('Woosh_1')
			else:
				sound.play_effect('Woosh_2')
			self.prows_revealed[k] = not self.prows_revealed[k]
			
	
	def touch_moved(self, touch):
		pass
	
	def touch_ended(self, touch):
		pass
			

run(HungarianPhrasebook())
