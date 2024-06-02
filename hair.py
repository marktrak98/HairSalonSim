from __future__ import annotations
from collections import defaultdict


class Hair:

    REGION_NAMES_SHORTENED = {
        'left bangs': 'bangs(L)',
        'right bangs': 'bangs(R)',
        'left sideburn': ' sideburn(L)',
        'right sideburn': 'sideburn(R)',
        'left top': 'top(L)',
        'right top': 'top(R)',
        'left above ears': ' above ears(L)',
        'right above ears': 'above ears(R)',
        'left crown': 'crown(L)',
        'right crown': 'crown(R)',
        'left behind ears': 'behind ears(L)',
        'right behind ears': 'behind ears(R)',
        'left back': ' back(L)',
        'right back': 'back(R)',
        'left nape': ' nape(L)',
        'right nape': 'nape(R)',
        '': ''
    }

    REGION_NAMES = [
        'left bangs',
        'right bangs',
        'left sideburn',
        'right sideburn',
        'left top',
        'right top',
        'left above ears',
        'right above ears',
        'left crown',
        'right crown',
        'left behind ears',
        'right behind ears',
        'left back',
        'right back',
        'left nape',
        'right nape'
    ]

    REGIONS_BY_POSITION = [
        [None, 'left bangs', 'right bangs', None],
        ['left sideburn', 'left top', 'right top', 'right sideburn'],
        ['left above ears', 'left crown', 'right crown', 'right above ears'],
        ['left behind ears', 'left back', 'right back', 'right behind ears'],
        [None, 'left nape', 'right nape', None]
    ]

    def __init__(self, starting_lengths: list[float]):
        self.left_bangs = Bangs('left bangs', starting_lengths[0])
        self.right_bangs = Bangs('right bangs', starting_lengths[1])
        self.left_sideburn = Sideburns('left sideburn', starting_lengths[2])
        self.right_sideburn = Sideburns('right sideburn', starting_lengths[3])
        self.left_top = Top('left top', starting_lengths[4])
        self.right_top = Top('right top', starting_lengths[5])
        self.left_above_ears = AboveEars('left above ears', starting_lengths[6])
        self.right_above_ears = AboveEars('right above ears', starting_lengths[7])
        self.left_crown = Crown('left crown', starting_lengths[8])
        self.right_crown = Crown('right crown', starting_lengths[9])
        self.left_behind_ears = BehindEars('left behind ears', starting_lengths[10])
        self.right_behind_ears = BehindEars('right behind ears', starting_lengths[11])
        self.left_back = Back('left back', starting_lengths[12])
        self.right_back = Back('right back', starting_lengths[13])
        self.left_nape = Nape('left nape', starting_lengths[14])
        self.right_nape = Nape('right nape', starting_lengths[15])

        self.sections: list[HairSection] = [
            self.left_bangs,
            self.right_bangs,
            self.left_sideburn,
            self.right_sideburn,
            self.left_top,
            self.right_top,
            self.left_above_ears,
            self.right_above_ears,
            self.left_crown,
            self.right_crown,
            self.left_behind_ears,
            self.right_behind_ears,
            self.left_back,
            self.right_back,
            self.left_nape,
            self.right_nape
        ]

        self.sections_by_position: list[list[HairSection|None]] = []
        for row in self.REGIONS_BY_POSITION:
            self.sections_by_position.append([])
            for region_name in row:
                self.sections_by_position[-1].append(self.get_region(region_name) if region_name else None)

        self.description = ''
        self.evaluate_description()

    def on_wash(self):
        for section in self.sections:
            section._wetness = 1

    def on_blow_dry(self):
        for section in self.sections:
            section._wetness = 0

    def get_region(self, region_name: str) -> HairSection:
        return getattr(self, region_name.replace(' ', '_'))

    def __getitem__(self, region_name: str):
        return self.get_region(region_name)
    
    def __str__(self) -> str:
        return str(self.description)
    
    def evaluate_description(self):
        #section_descriptions = {section.region_name: section.length_description for section in self.sections}
        
        section_descriptions_dict = defaultdict(lambda : [])
        for section in self.sections:
            section_descriptions_dict[section.length_description].append(section.region_name)

        section_descriptions_list = list(section_descriptions_dict.items())
        section_descriptions_list.sort(key=lambda x: len(x[1]), reverse=False)

        self.description = ''
        if len(section_descriptions_list) == 1:
            desc, region_names = section_descriptions_list[-1]
            self.description += f'{desc}'

        else:
            for desc, region_names in section_descriptions_list[:-1]:
                if len(region_names) >= 2:
                    self.description += f'{", ".join(region_names)} are {desc}'
                else:
                    self.description += f'{", ".join(region_names)} is {desc}'
                
                self.description += '; '

            desc, region_names = section_descriptions_list[-1]
            self.description = self.description[:-2] + f' and rest is {desc}'
        
    @classmethod
    def new(cls, starting_lengths=None):
        if starting_lengths is None:
            starting_lengths = [20.0] * len(cls.REGION_NAMES)
            
        return cls(starting_lengths)



class HairSection:

    LENGTH_RANGES = [
            ('bald', 0),
            ('buzzed(1/16th inch)', 0.0625),
            ('buzzed(1/8th inch)', 0.125),
            ('buzzed(1/4th inch)', 0.25),
            ('buzzed to 1/2 an inch', 0.5),
            ('cropped', 1),
            ('longish crop', 2),
            ('eyebrow length', 4),
            ('ear length', 6),
            ('lip length', 8),
            ('chin length', 10),
            ('touching shoulders', 12),
            ('below shoulders', 16),
            ('midback length', 20),
            ('waist length', 24),
            ('beyond waist', float('inf'))
    ]

    def __init__(self, region_name: str, length: float):
        self.region_name: str = region_name
        
        self._length: float = length # in inches
        self._intrinsic_growth_rate: float = 0.1  # length per health per day
        self._health: float = 1  # Between 0(unhealthy) and 1(healthy)
        self._wetness: float = 0  # Between 0(dry) and 1(drenched)
        self._glossiness: float = 0  # Between 0(dry) and 1(drenched)

    @property
    def length_description(self):
        for length, max_length in self.LENGTH_RANGES:
            if self._length <= max_length:
                return length

        raise NotImplementedError

    @property
    def growth_rate(self):
        return self._intrinsic_growth_rate * self._health

    def grow(self, days_passed):
        self._length += self.growth_rate + days_passed


class Bangs(HairSection):
    LENGTH_RANGES = [
        ('bald', 0),
        ('buzzed(1/16th inch)', 0.0625),
        ('buzzed(1/8th inch)', 0.125),
        ('buzzed(1/4th inch)', 0.25),
        ('microbangs', 0.5),
        ('halfway down forehead', 1),
        ('eyebrow length', 2),
        ('eye length', 2.5),
        ('nose length', 3),
        ('lip length', 5),
        ('chin length', 7),
        ('touching shoulders', 10),
        ('below shoulders', 14),
        ('midback length', 25),
        ('waist length', 40),
        ('beyond waist', float('inf'))
    ]


class Sideburns(HairSection):
    LENGTH_RANGES = [
        ('bald', 0),
        ('buzzed(1/16th inch)', 0.0625),
        ('buzzed(1/8th inch)', 0.125),
        ('buzzed(1/4th inch)', 0.25),
        ('buzzed(1/2th inch)', 0.5),
        ('cropped', 1),
        ('longish crop', 2),
        ('lip length', 3),
        ('chin length', 4),
        ('touching shoulders', 7),
        ('below shoulders', 11),
        ('midback length', 22),
        ('waist length', 37),
        ('beyond waist', float('inf'))
    ]


class Top(HairSection):
    LENGTH_RANGES = [
        ('bald', 0),
        ('buzzed(1/16th inch)', 0.0625),
        ('buzzed(1/8th inch)', 0.125),
        ('buzzed(1/4th inch)', 0.25),
        ('buzzed(1/2th inch)', 0.5),
        ('cropped', 2),
        ('longish crop', 4),
        ('eye length', 5.5),
        ('nose length', 6),
        ('lip length', 8),
        ('chin length', 10),
        ('touching shoulders', 13),
        ('below shoulders', 17),
        ('midback length', 28),
        ('waist length', 43),
        ('beyond waist', float('inf'))
    ]


class AboveEars(HairSection):
    LENGTH_RANGES = [
        ('bald', 0),
        ('buzzed(1/16th inch)', 0.0625),
        ('buzzed(1/8th inch)', 0.125),
        ('buzzed(1/4th inch)', 0.25),
        ('buzzed(1/2th inch)', 0.5),
        ('cropped', 1),
        ('longish crop', 2),
        ('lip length', 3),
        ('chin length', 4),
        ('touching shoulders', 7),
        ('below shoulders', 11),
        ('midback length', 22),
        ('waist length', 37),
        ('beyond waist', float('inf'))
    ]


class Crown(HairSection):
    LENGTH_RANGES = [
        ('bald', 0),
        ('buzzed(1/16th inch)', 0.0625),
        ('buzzed(1/8th inch)', 0.125),
        ('buzzed(1/4th inch)', 0.25),
        ('buzzed(1/2th inch)', 0.5),
        ('cropped', 2),
        ('longish crop', 4),
        ('eyebrow length', 5),
        ('eye length', 5.5),
        ('nose length', 6),
        ('lip length', 8),
        ('chin length', 10),
        ('touching shoulders', 13),
        ('below shoulders', 17),
        ('midback length', 28),
        ('waist length', 43),
        ('beyond waist', float('inf'))
    ]


class BehindEars(HairSection):
    LENGTH_RANGES = [
        ('bald', 0),
        ('buzzed(1/16th inch)', 0.0625),
        ('buzzed(1/8th inch)', 0.125),
        ('buzzed(1/4th inch)', 0.25),
        ('buzzed(1/2th inch)', 0.5),
        ('cropped', 1),
        ('longish crop', 2),
        ('lip length', 3),
        ('chin length', 4),
        ('touching shoulders', 7),
        ('below shoulders', 11),
        ('midback length', 22),
        ('waist length', 37),
        ('beyond waist', float('inf'))
    ]


class Back(HairSection):
    LENGTH_RANGES = [
        ('bald', 0),
        ('buzzed(1/16th inch)', 0.0625),
        ('buzzed(1/8th inch)', 0.125),
        ('buzzed(1/4th inch)', 0.25),
        ('buzzed(1/2th inch)', 0.5),
        ('cropped', 1),
        ('longish crop', 2),
        ('lip length', 3),
        ('chin length', 4),
        ('touching shoulders', 7),
        ('below shoulders', 11),
        ('midback length', 22),
        ('waist length', 37),
        ('beyond waist', float('inf'))
    ]


class Nape(HairSection):
    LENGTH_RANGES = [
        ('bald', 0),
        ('buzzed(1/16th inch)', 0.0625),
        ('buzzed(1/8th inch)', 0.125),
        ('buzzed(1/4th inch)', 0.25),
        ('buzzed(1/2th inch)', 0.5),
        ('lip length', 1),
        ('chin length', 4),
        ('touching shoulders', 7),
        ('below shoulders', 11),
        ('midback length', 22),
        ('waist length', 37),
        ('beyond waist', float('inf'))
    ]

