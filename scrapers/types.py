from enum import Enum

# WARNING
# Enums must be treated as append-only in production.
# To maintain backward compatibility with frontend URIs,
# do not modify or remove existing values!

class Category(Enum):
    NONE = 1
    MEAT_AND_FISH = 2
    FRUITS_AND_VEGETABLES = 3
    DAIRY_AND_EGGS = 4
    BAKERY = 5
    DRINKS = 6
    PANTRY_STAPLES = 7
    HYGIENE_PRODUCTS = 8
    SPORTS = 9
    RECREATION = 10
    TRANSPORTATION = 11
    HOUSING = 12

class Unit(Enum):
    NONE = 1
    KG = 2
    L = 3
    EACH = 4
    MONTHLY = 5
    YEARLY = 6
    MONTHLY_M2 = 7
    KWH = 8
    M3 = 9

class Country(Enum):
    NONE = 1
    HU = 2
    DK = 3

class Lang(Enum):
    EN = 1
    HU = 2
    DK = 3

class Currency(Enum):
    EUR = 1
    HUF = 2
    DKK = 3

class Aggregate(Enum):
    MEAN = 1
    MIN = 2
    MAX = 3

class Item(Enum):
    CHICKEN_BREAST_FILLET = 1
    BEEF_MINCE = 2
    PORK_MINCE = 3
    APPLE = 4
    BANANA = 5
    ORANGE = 6
    LEMON = 7
    RASPBERRY = 8
    BLUEBERRY = 9
    TOMATO = 10
    PEPPER = 11
    POTATO = 12
    SWEET_POTATO = 13
    CARROT = 14
    ONION = 15
    GARLIC = 16
    MILK = 17
    BUTTER = 18
    CHEESE = 19
    EGG = 20
    BREAD = 21
    GLUTEN_FREE_BREAD = 22
    WATER = 23
    COKE = 24
    ENERGY_DRINK = 25
    BEER = 26
    FLOUR = 27
    SUGAR = 28
    SALT = 29
    OLIVE_OIL = 30
    SUNFLOWER_OIL = 31
    RICE = 32
    SPAGHETTI_PASTA = 33
    RED_BEANS_CAN = 34
    CRUMBLED_SWEET_CORN_CAN = 35
    SHAMPOO = 36
    SOAP = 37
    TOOTHPASTE = 38
    TAMPON = 39
    CONDOM = 40
    TOILET_PAPER = 41
    GYM_SINGLE_ENTRANCE = 42
    GYM_MONTHLY_MEMBERSHIP = 43
    GYM_YEARLY_MEMBERSHIP = 44
    CLIMBING_GYM_SINGLE_ENTRANCE = 45
    CLIMBING_GYM_MONTHLY_MEMBERSHIP = 46
    CLIMBING_GYM_YEARLY_MEMBERSHIP = 47
    EATING_OUT = 48
    FAST_FOOD = 49
    MOVIE_TICKET = 50
    CAR_DIESEL = 51
    CAR_GASOLINE = 52
    CAR_HIGHWAY_YEARLY = 53
    PUBLIC_TRANSPORT_SINGLE_TICKET = 54
    PUBLIC_TRANSPORT_MONTHLY_CITY_PASS = 55
    PUBLIC_TRANSPORT_YEARLY_CITY_PASS = 56
    PUBLIC_TRANSPORT_MONTHLY_COUNTRY_PASS = 57
    PUBLIC_TRANSPORT_YEARLY_COUNTRY_PASS = 58
    RENT_CAPITAL_CITY_CENTER = 59
    UTILITY_ELECTRICITY = 60
    UTILITY_WATER = 61
    UTILITY_GAS = 62

util_category_fruits = [
    Item.APPLE,
    Item.BANANA,
    Item.ORANGE,
    Item.LEMON,
    Item.RASPBERRY,
    Item.BLUEBERRY,
]
util_category_vegetables = [
    Item.TOMATO,
    Item.PEPPER,
    Item.POTATO,
    Item.SWEET_POTATO,
    Item.CARROT,
    Item.ONION,
    Item.GARLIC,
]

lookup_currency = {
    Country.HU: Currency.HUF,
    Country.DK: Currency.DKK,
}

lookup_filters = {
    Item.CHICKEN_BREAST_FILLET: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.MEAT_AND_FISH,
        Lang.EN: ([["chicken","breast","fill"]],["bio"]),
        Lang.HU: ([["csirke","mell","filé"]],["bio", "GMO"]),
        Lang.DK: ([["kylling","bryst","filet"]],["bio", "GMO", "øko"]),
    },
    Item.BEEF_MINCE: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.MEAT_AND_FISH,
        Lang.EN: ([["beef","mince"],["beef","ground"]],["bio", "pork"]),
        Lang.HU: ([["marha","darált","hús"]],["bio", "sertés", "GMO"]),
        Lang.DK: ([["hakket","okse"]],["bio", "grise", "GMO", "øko"]),
    },
    Item.PORK_MINCE: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.MEAT_AND_FISH,
        Lang.EN: ([["pork","mince"],["pork","ground"]],["bio", "beef"]),
        Lang.HU: ([["sertés","darált","hús"]],["bio", "marha", "GMO"]),
        Lang.DK: ([["hakket","grise"]],["bio", "okse", "GMO", "øko"]),
    },
    Item.APPLE: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["apple"]],["olive", "snack", "frozen", "freeze", "choco", "pickled", "pineapple"]),
        Lang.HU: ([["alma"]],["gránát"]),
        Lang.DK: ([["æble"]],["granat", "must"]),
    },
    Item.BANANA: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["banana"]],["olive", "snack", "frozen", "freeze", "choco", "pickled"]),
        Lang.HU: ([["banán"]],[]),
        Lang.DK: ([["banan"]],["must"]),
    },
    Item.ORANGE: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["orange"]],["olive", "snack", "frozen", "freeze", "choco", "pickled"]),
        Lang.HU: ([["narancs"]],[]),
        Lang.DK: ([["appelsin"]],["must"]),
    },
    Item.LEMON: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["lemon"]],["olive", "snack", "frozen", "freeze", "choco", "pickled"]),
        Lang.HU: ([["citrom"]],[]),
        Lang.DK: ([["citron"]],["must"]),
    },
    Item.RASPBERRY: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["raspberr"]],["olive", "snack", "frozen", "freeze", "choco", "pickled"]),
        Lang.HU: ([["málna"]],[]),
        Lang.DK: ([["hindbær"]],["must"]),
    },
    Item.BLUEBERRY: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["blueberr"]],["olive", "snack", "frozen", "freeze", "choco", "pickled"]),
        Lang.HU: ([["áfonya"]],[]),
        Lang.DK: ([["blåbær"]],["must"]),
    },
    Item.TOMATO: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["tomato"]],["olive", "snack", "baby", "can", "dried", "pickled"]),
        Lang.HU: ([["paradicsom"]],[]),
        Lang.DK: ([["tomater"]],["must"]),
    },
    Item.PEPPER: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["bell","pepper"],["california","paprika"],["california","pepper"],["tv paprika"],["szentesi","paprika"],["capia","paprika"],["banana","pepper"]],["snack", "white", "black", "can", "olive", "pickled"]),
        Lang.HU: ([["kaliforniai","paprika"],["étkezési","paprika"]],[]),
        Lang.DK: ([["peber"]],["peberrod","peberkorn","tapas"]),
    },
    Item.POTATO: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["potato"]],["sweet", "snack", "pickled"]),
        Lang.HU: ([["burgonya"]],["édes"]),
        Lang.DK: ([["kartofler"]],["søde"]),
    },
    Item.SWEET_POTATO: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["sweet","potato"]],["snack", "pickled"]),
        Lang.HU: ([["édes","burgonya"]],[]),
        Lang.DK: ([["søde","kartofler"]],[]),
    },
    Item.CARROT: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["carrot"]],["baby", "can", "snack", "pickled"]),
        Lang.HU: ([["sárga", "répa"]],[]),
        Lang.DK: ([["gulerødder"]],["must", "snack", "salat"]),
    },
    Item.ONION: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["onion"]],["sweet", "snack", "pickled", "spring"]),
        Lang.HU: ([["vörös","hagyma"],["lila","hagyma"]],[]),
        Lang.DK: ([["løg"]],["hvid","purløg","ramsløg"]),
    },
    Item.GARLIC: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.FRUITS_AND_VEGETABLES,
        Lang.EN: ([["garlic"]],["olive", "nut", "snack", "pickled"]),
        Lang.HU: ([["fok","hagyma"]],[]),
        Lang.DK: ([["hvidløg"]],["spirer"]),
    },
    Item.MILK: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.DAIRY_AND_EGGS,
        Lang.EN: ([["milk"]],["goat", "sheep", "lactose", "coco", "vanilla", "coffe", "drink"]),
        Lang.HU: ([["tej"]],["kecske", "juh", "aludt", "laktóz", "kakó", "vanília", "kávé", "ital"]),
        Lang.DK: ([["mælk"]],["ged", "får", "laktose", "portioner"]),
    },
    Item.BUTTER: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.DAIRY_AND_EGGS,
        Lang.EN: ([["butter"]],["goat", "sheep", "lactose", "cream", "spread"]),
        Lang.HU: ([["vaj"]],["kecske", "juh", "laktóz", "krém", "fűszer", "sajt"]),
        Lang.DK: ([["smør"]],["ged", "får", "laktose", "løg", "ost"]),
    },
    Item.CHEESE: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.DAIRY_AND_EGGS,
        Lang.EN: ([["cheese"]],["goat", "sheep", "lactose", "sliced", "spread", "vegan", "grated"]),
        Lang.HU: ([["sajt"]],["kecske", "juh", "laktóz", "szeletelt", "krém", "kenhető", "hagym", "habos", "reszelt"]),
        Lang.DK: ([["cheddar"],["gouda"],["mozzarella"],["emmentaler"]],["ged", "får", "laktose", "løg", "ost"]),
    },
    Item.EGG: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.DAIRY_AND_EGGS,
        Lang.EN: ([["egg"],["tojás"]],["fürj"]),
        Lang.HU: ([["tojás"]],[]),
        Lang.DK: ([["æg"]],[]),
    },
    Item.BREAD: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.BAKERY,
        Lang.EN: ([["bread"],["loaf"]],["gluten", "free"]),
        Lang.HU: (),
        Lang.DK: ([["brød"]],["snack", "gluten"]),
    },
    Item.GLUTEN_FREE_BREAD: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.BAKERY,
        Lang.EN: ([["gluten", "free", "bread"],["gluten", "free", "loaf"]],[]),
        Lang.HU: (),
        Lang.DK: ([["glutenfri", "brød"]],["snack"]),
    },
    Item.WATER: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.DRINKS,
        Lang.EN: ([["mineral", "water"]],["drink", "energy", "beverage", "soda", "flavo"]),
        Lang.HU: (),
        Lang.DK: ([["vand"]],[]),
    },
    Item.COKE: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.DRINKS,
        Lang.EN: ([["coca", "cola"],["pepsi"]],[]),
        Lang.HU: (),
        Lang.DK: ([["coca", "cola"],["pepsi"]],[]),
    },
    Item.ENERGY_DRINK: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.DRINKS,
        Lang.EN: ([["hell", "energy"],["red bull"],["redbull"]],["beer"]),
        Lang.HU: (),
        Lang.DK: ([["red bull"],["redbull"]],[]),
    },
    Item.BEER: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.DRINKS,
        Lang.EN: ([["beer"]],["non", "free"]),
        Lang.HU: (),
        Lang.DK: ([["tuborg"],["heineken"],["carlsberg"],["blanc"],["ipa"],["stout"],["royal classic"],["royal export"],["leffe"]],["fri"]),
    },
    Item.FLOUR: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["flour"]],["with","szafi"]),
        Lang.HU: (),
        Lang.DK: ([["mel"]],["malt","ris"]),
    },
    Item.SUGAR: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["sugar"]],["with","vanil","powdered","cube","icing","brown","coco"]),
        Lang.HU: (),
        Lang.DK: ([["sukker"]],["brun","koko","mørk","nalder","bland","sticks"]),
    },
    Item.SALT: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["salt"]],["with","salted","seasoned","salty","spice","himalaya","ropi","sticks"]),
        Lang.HU: ([["só"]],["ropi"]),
        Lang.DK: ([["salt"]],["chili","himalaya"]),
    },
    Item.OLIVE_OIL: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["olive","oil"]],[" in "]),
        Lang.HU: (),
        Lang.DK: ([["oliven","olie"]],["solsikke"]),
    },
    Item.SUNFLOWER_OIL: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["sunflower","oil"]],[" in "]),
        Lang.HU: (),
        Lang.DK: ([["solsikke","olie"]],["oliven"]),
    },
    Item.RICE: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["rice"]],["with"]),
        Lang.HU: (),
        Lang.DK: ([["ris"]],["røde"]),
    },
    Item.SPAGHETTI_PASTA: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["spaghetti","dry","pasta"]],["gluten"]),
        Lang.HU: (),
        Lang.DK: ([["spaghett"]],["gluten"]),
    },
    Item.RED_BEANS_CAN: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["red","bean","brine"],["red","bean","kidney"],["bonduelle","bean"]],["chilli","corn"]),
        Lang.HU: (),
        Lang.DK: ([["røde","kidney","bønner"]],["chili","majs"]),
    },
    Item.CRUMBLED_SWEET_CORN_CAN: {
        Unit.NONE: Unit.KG,
        Category.NONE: Category.PANTRY_STAPLES,
        Lang.EN: ([["sweet","corn","brine"],["sweet","corn","bonduelle"]],["bean","popcorn","flavo"]),
        Lang.HU: (),
        Lang.DK: ([["majs"]],["baby","kolber"]),
    },
    Item.SHAMPOO: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.HYGIENE_PRODUCTS,
        Lang.EN: ([["shampoo"]],[]),
        Lang.HU: (),
        Lang.DK: ([["shampoo"]],["balsam"]),
    },
    Item.SOAP: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.HYGIENE_PRODUCTS,
        Lang.EN: ([["soap"]],[]),
        Lang.HU: (),
        Lang.DK: ([["sæbe"]],[]),
    },
    Item.TOOTHPASTE: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.HYGIENE_PRODUCTS,
        Lang.EN: ([["toothpaste"]],[]),
        Lang.HU: (),
        Lang.DK: ([["tandpasta"]],["børn"]),
    },
    Item.TAMPON: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.HYGIENE_PRODUCTS,
        Lang.EN: ([["tampon"]],[]),
        Lang.HU: (),
        Lang.DK: ([["tampon"]],["bind"]),
    },
    Item.CONDOM: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.HYGIENE_PRODUCTS,
        Lang.EN: ([["condom"]],["lube"]),
        Lang.HU: (),
        Lang.DK: ([["kondom"]],[]),
    },
    Item.TOILET_PAPER: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.HYGIENE_PRODUCTS,
        Lang.EN: ([["toilet","paper"]],["wet","sensitive","kid","moist","moddia"]),
        Lang.HU: (),
        Lang.DK: ([["toilet","papir"]],["fugtigt"]),
    },
    Item.GYM_SINGLE_ENTRANCE: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.SPORTS,
        Lang.EN: (),
        Lang.HU: ([["napijegy","1 alkalom"],["flexgym felnőtt","1 alkalom"],["nemes fitness","napijegy"],["fitness budapest","1-entry pass"]],["diák","nyugdíjas","gyermek"]),
        Lang.DK: ([["puregym","dagskort"],["fitnessx","dagspas"],["vesterbronx","day pass"]],[]),
    },
    Item.GYM_MONTHLY_MEMBERSHIP: {
        Unit.NONE: Unit.MONTHLY,
        Category.NONE: Category.SPORTS,
        Lang.EN: (),
        Lang.HU: ([["bérlet","felnőtt","1 hónap"],["flexgym felnőtt","1 havi"],["nemes fitness","1 hónap"],["fitness budapest","normal pass"]],["diák","nyugdíjas","napijegy","alkalom","gyermek"]),
        Lang.DK: ([["puregym","månedlig"],["fitnessx","månedlig"],["vesterbronx","medlemskab"]],[]),
    },
    Item.GYM_YEARLY_MEMBERSHIP: {
        Unit.NONE: Unit.YEARLY,
        Category.NONE: Category.SPORTS,
        Lang.EN: (),
        Lang.HU: ([["bérlet","felnőtt","12 hónap"],["flexgym felnőtt","1 éves"]],["diák","nyugdíjas","napijegy","alkalom","gyermek"]),
        Lang.DK: ([["puregym","årlig"],["fitnessx","årlig"]],[]),
    },
    Item.CLIMBING_GYM_SINGLE_ENTRANCE: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.SPORTS,
        Lang.EN: (),
        Lang.HU: ([["monkeyboulder","felnőtt","napi"],["gravityboulder","csúcsidőszak","belépő"],["gravityboulder","völgyidő","belépő"],["flowboulder","felnőtt","belépő"]],["bérlet"]),
        Lang.DK: ([["betaboulders","single pass"],["bisonboulders","day ticket"],["boulders","dagsentré og udstyr"]],[]),
    },
    Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP: {
        Unit.NONE: Unit.MONTHLY,
        Category.NONE: Category.SPORTS,
        Lang.EN: (),
        Lang.HU: ([["monkeyboulder","felnőtt","bérlet","havi"],["gravityboulder","bérlet","1 hónap"],["flowboulder","bérlet","havi"]],["éves","féléves","negyedéves"]),
        Lang.DK: ([["betaboulders","monthly"],["bisonboulders","monthly"],["bisonboulders","30 days pass"],["boulders","medlemskab"]],[]),
    },
    Item.CLIMBING_GYM_YEARLY_MEMBERSHIP: {
        Unit.NONE: Unit.YEARLY,
        Category.NONE: Category.SPORTS,
        Lang.EN: (),
        Lang.HU: ([["monkeyboulder","felnőtt","bérlet","éves"],["gravityboulder","bérlet","12 hónap"],["flowboulder","bérlet","éves"]],["féléves","negyedéves","havi"]),
        Lang.DK: ([["betaboulders","yearly"],["bisonboulders","yearly"]],[]),
    },
    Item.EATING_OUT: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.RECREATION,
        Lang.EN: ([[""]],[]),
        Lang.HU: ([[""]],[]),
        Lang.DK: ([[""]],[]),
    },
    Item.FAST_FOOD: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.RECREATION,
        Lang.EN: ([["mcdonald"]],[]),
        Lang.HU: ([["mcdonald"]],[]),
        Lang.DK: ([["mcdonald"]],[]),
    },
    Item.MOVIE_TICKET: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.RECREATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.CAR_DIESEL: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.TRANSPORTATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.CAR_GASOLINE: {
        Unit.NONE: Unit.L,
        Category.NONE: Category.TRANSPORTATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.CAR_HIGHWAY_YEARLY: {
        Unit.NONE: Unit.YEARLY,
        Category.NONE: Category.TRANSPORTATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.PUBLIC_TRANSPORT_SINGLE_TICKET: {
        Unit.NONE: Unit.EACH,
        Category.NONE: Category.TRANSPORTATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.PUBLIC_TRANSPORT_MONTHLY_CITY_PASS: {
        Unit.NONE: Unit.MONTHLY,
        Category.NONE: Category.TRANSPORTATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.PUBLIC_TRANSPORT_YEARLY_CITY_PASS: {
        Unit.NONE: Unit.YEARLY,
        Category.NONE: Category.TRANSPORTATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.PUBLIC_TRANSPORT_MONTHLY_COUNTRY_PASS: {
        Unit.NONE: Unit.MONTHLY,
        Category.NONE: Category.TRANSPORTATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.PUBLIC_TRANSPORT_YEARLY_COUNTRY_PASS: {
        Unit.NONE: Unit.YEARLY,
        Category.NONE: Category.TRANSPORTATION,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.RENT_CAPITAL_CITY_CENTER: {
        Unit.NONE: Unit.MONTHLY_M2,
        Category.NONE: Category.HOUSING,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.UTILITY_ELECTRICITY: {
        Unit.NONE: Unit.KWH,
        Category.NONE: Category.HOUSING,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.UTILITY_WATER: {
        Unit.NONE: Unit.M3,
        Category.NONE: Category.HOUSING,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
    Item.UTILITY_GAS: {
        Unit.NONE: Unit.M3,
        Category.NONE: Category.HOUSING,
        Lang.EN: (),
        Lang.HU: (),
        Lang.DK: (),
    },
}

def enum_to_string(obj, language=Lang.EN):
    if isinstance(obj, Currency):
        return obj.name
    if language == Lang.EN:
        if isinstance(obj, Category):
            if obj == Category.MEAT_AND_FISH:
                return "Meat and Fish"
            if obj == Category.FRUITS_AND_VEGETABLES:
                return "Fruits and Vegetables"
            if obj == Category.DAIRY_AND_EGGS:
                return "Dairy and Eggs"
            if obj == Category.BAKERY:
                return "Bakery"
            if obj == Category.DRINKS:
                return "Drinks"
            if obj == Category.PANTRY_STAPLES:
                return "Pantry Staples"
            if obj == Category.HYGIENE_PRODUCTS:
                return "Hygiene Products"
            if obj == Category.SPORTS:
                return "Sports"
            if obj == Category.RECREATION:
                return "Recreation"
            if obj == Category.TRANSPORTATION:
                return "Transportation"
            if obj == Category.HOUSING:
                return "Housing"
        if isinstance(obj, Unit):
            if obj == Unit.KG:
                return "kg"
            elif obj == Unit.L:
                return "l"
            elif obj == Unit.EACH:
                return "each"
            elif obj == Unit.MONTHLY:
                return "month"
            elif obj == Unit.YEARLY:
                return "year"
            elif obj == Unit.MONTHLY_M2:
                return "month m<sup>2</sup>"
            elif obj == Unit.KWH:
                return "kwh"
            elif obj == Unit.M3:
                return "m<sup>3</sup>"
        if isinstance(obj, Country):
            if obj == Country.HU:
                return "Hungary"
            if obj == Country.DK:
                return "Denmark"
        if isinstance(obj, Lang):
            if obj == Lang.EN:
                return "English"
            if obj == Lang.HU:
                return "Hungarian"
            if obj == Lang.DK:
                return "Danish"
        if isinstance(obj, Aggregate):
            if obj == Aggregate.MEAN:
                return "Average"
            if obj == Aggregate.MIN:
                return "Min"
            if obj == Aggregate.MAX:
                return "Max"
        if isinstance(obj, Item):
            if obj == Item.CHICKEN_BREAST_FILLET:
                return "Chicken Breast Fillet"
            if obj == Item.BEEF_MINCE:
                return "Beef Mince"
            if obj == Item.PORK_MINCE:
                return "Pork Mince"
            if obj == Item.APPLE:
                return "Apple"
            if obj == Item.BANANA:
                return "Banana"
            if obj == Item.ORANGE:
                return "Orange"
            if obj == Item.LEMON:
                return "Lemon"
            if obj == Item.RASPBERRY:
                return "Raspberry"
            if obj == Item.BLUEBERRY:
                return "Blueberry"
            if obj == Item.TOMATO:
                return "Tomato"
            if obj == Item.PEPPER:
                return "Pepper"
            if obj == Item.POTATO:
                return "Potato"
            if obj == Item.SWEET_POTATO:
                return "Sweet Potato"
            if obj == Item.CARROT:
                return "Carrot"
            if obj == Item.ONION:
                return "Onion"
            if obj == Item.GARLIC:
                return "Garlic"
            if obj == Item.MILK:
                return "Milk"
            if obj == Item.BUTTER:
                return "Butter"
            if obj == Item.CHEESE:
                return "Cheese"
            if obj == Item.EGG:
                return "Egg"
            if obj == Item.BREAD:
                return "Bread"
            if obj == Item.GLUTEN_FREE_BREAD:
                return "Gluten Free Bread"
            if obj == Item.WATER:
                return "Water"
            if obj == Item.COKE:
                return "Coke"
            if obj == Item.ENERGY_DRINK:
                return "Energy Drink"
            if obj == Item.BEER:
                return "Beer"
            if obj == Item.FLOUR:
                return "Flour"
            if obj == Item.SUGAR:
                return "Sugar"
            if obj == Item.SALT:
                return "Salt"
            if obj == Item.OLIVE_OIL:
                return "Olive Oil"
            if obj == Item.SUNFLOWER_OIL:
                return "Sunflower Oil"
            if obj == Item.RICE:
                return "Rice"
            if obj == Item.SPAGHETTI_PASTA:
                return "Spaghetti Dry Pasta"
            if obj == Item.RED_BEANS_CAN:
                return "Canned Red Beans"
            if obj == Item.CRUMBLED_SWEET_CORN_CAN:
                return "Canned Sweet Corn"
            if obj == Item.SHAMPOO:
                return "Shampoo"
            if obj == Item.SOAP:
                return "Soap"
            if obj == Item.TOOTHPASTE:
                return "Toothpaste"
            if obj == Item.TAMPON:
                return "Tampon"
            if obj == Item.CONDOM:
                return "Condom"
            if obj == Item.TOILET_PAPER:
                return "Toilet Paper Roll"
            if obj == Item.GYM_SINGLE_ENTRANCE:
                return "Gym - Single Entrance"
            if obj == Item.GYM_MONTHLY_MEMBERSHIP:
                return "Gym - Monthly Membership"
            if obj == Item.GYM_YEARLY_MEMBERSHIP:
                return "Gym - Yearly Membership"
            if obj == Item.CLIMBING_GYM_SINGLE_ENTRANCE:
                return "Bouldering Gym - Single Entrance"
            if obj == Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP:
                return "Bouldering Gym - Monthly Membership"
            if obj == Item.CLIMBING_GYM_YEARLY_MEMBERSHIP:
                return "Bouldering Gym - Yearly Membership"
            if obj == Item.EATING_OUT:
                return "Eating Out - Restaurant"
            if obj == Item.FAST_FOOD:
                return "Eating Out - Fast Food"
            if obj == Item.MOVIE_TICKET:
                return "Movie Ticket"
            if obj == Item.CAR_DIESEL:
                return "Diesel"
            if obj == Item.CAR_GASOLINE:
                return "Gasoline"
            if obj == Item.CAR_HIGHWAY_YEARLY:
                return "Yearly Highway Pass"
            if obj == Item.PUBLIC_TRANSPORT_SINGLE_TICKET:
                return "Public Transport - Single Ticket"
            if obj == Item.PUBLIC_TRANSPORT_MONTHLY_CITY_PASS:
                return "Public Transport - Monthly City Pass"
            if obj == Item.PUBLIC_TRANSPORT_YEARLY_CITY_PASS:
                return "Public Transport - Yearly City Pass"
            if obj == Item.PUBLIC_TRANSPORT_MONTHLY_COUNTRY_PASS:
                return "Public Transport - Monthly Country Pass"
            if obj == Item.PUBLIC_TRANSPORT_YEARLY_COUNTRY_PASS:
                return "Public Transport - Yearly Country Pass"
            if obj == Item.RENT_CAPITAL_CITY_CENTER:
                return "Rent - City Center Capital City"
            if obj == Item.UTILITY_ELECTRICITY:
                return "Utility - Electricity"
            if obj == Item.UTILITY_WATER:
                return "Utility - Water"
            if obj == Item.UTILITY_GAS:
                return "Utility - Gas"
    return None

def parse_enum(text):
    splitted = text.split('.')
    base = splitted[0]
    name = splitted[1]
    if base == "Category":
        return Category[name]
    if base == "Unit":
        return Unit[name]
    if base == "Country":
        return Country[name]
    if base == "Lang":
        return Lang[name]
    if base == "Currency":
        return Currency[name]
    if base == "Item":
        return Item[name]