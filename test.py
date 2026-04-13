import importlib.util
import warnings
import pytest
import pandas as pd

from scrapers.items import Category, Unit, Country, Lang, Aggregate, Item, enum_to_string, lookup_filters


testdata = [
    (list(Category)[1:], Lang.EN),
    (list(Unit)[1:], Lang.EN),
    (list(Country)[1:], Lang.EN),
    (list(Lang), Lang.EN),
    (list(Aggregate), Lang.EN),
    (list(Item), Lang.EN),
]
@pytest.mark.parametrize("enums,language", testdata)
def test_translations(enums, language):
    missing = []
    for e in enums:
        if enum_to_string(e, language) is None:
            missing.append(e)
    if len(missing) > 0:
        raise Exception(f"Items {missing} has no {language} translation!")

groceries = [Category.MEAT_AND_FISH,Category.FRUITS_AND_VEGETABLES,Category.DAIRY_AND_EGGS,Category.BAKERY,Category.DRINKS,Category.PANTRY_STAPLES,Category.HYGIENE_PRODUCTS]
gym = [Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP,Item.GYM_YEARLY_MEMBERSHIP]
climbing_gym = [Item.CLIMBING_GYM_SINGLE_ENTRANCE,Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP,Item.CLIMBING_GYM_YEARLY_MEMBERSHIP]

testdata = [
    ("hungary/auchan.py",groceries),
    ("hungary/kifli.py",groceries),
    ("hungary/tesco.py",groceries),
    ("hungary/peakgym.py",gym),
    ("hungary/flexgym.py",gym),
    ("hungary/nemesfitness.py",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP]),
    ("hungary/4pfitness.py",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP]),
    ("hungary/monkeyboulder.py",climbing_gym),
    ("hungary/gravityboulder.py",climbing_gym),
    ("hungary/flowboulder.py",climbing_gym),
    ("denmark/bilka.py",groceries),
    ("denmark/nemlig.py",groceries),
    ("denmark/puregym.py",[Item.GYM_MONTHLY_MEMBERSHIP,Item.GYM_YEARLY_MEMBERSHIP]),
    ("denmark/fitnessx.py",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP]),
    ("denmark/vesterbronxgym.py",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP]),
    ("denmark/betaboulders.py",climbing_gym),
    ("denmark/bisonboulders.py",climbing_gym),
    ("denmark/boulders.py",[Item.CLIMBING_GYM_SINGLE_ENTRANCE,Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP]),
]
@pytest.mark.parametrize("module_path,categories", testdata)
def test_sources(module_path, categories):
    spec = importlib.util.spec_from_file_location(module_path, "scrapers/"+module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    df = module.get_items()
    items_req = [c for c in categories if isinstance(c, Item)]
    categories = [c for c in categories if isinstance(c, Category)]
    for item in lookup_filters:
        if lookup_filters[item][Category.NONE] in categories:
            items_req.append(item)
    items_req = set(items_req)
    items_df = set(df["name"])
    missing_items = list(items_req - items_df)
    if len(missing_items) > 0:
        warnings.warn(UserWarning(f"Items {missing_items} are not scraped by {module_path}!"))

testdata = [
    (Country.HU, ["hungary/tesco.py","hungary/kifli.py","hungary/auchan.py"],groceries),
    (Country.HU, ["hungary/peakgym.py","hungary/flexgym.py","hungary/nemesfitness.py","hungary/4pfitness.py"],gym),
    (Country.HU, ["hungary/monkeyboulder.py","hungary/gravityboulder.py","hungary/flowboulder.py"],climbing_gym),
    (Country.DK, ["denmark/bilka.py","denmark/nemlig.py"],groceries),
    (Country.HU, ["denmark/puregym.py","denmark/fitnessx.py","denmark/vesterbronxgym.py"],gym),
    (Country.HU, ["denmark/betaboulders.py","denmark/bisonboulders.py","denmark/boulders.py"],climbing_gym),
]
@pytest.mark.parametrize("country,module_paths,categories", testdata)
def test_country(country, module_paths, categories):
    df = None
    for module_path in module_paths:
        spec = importlib.util.spec_from_file_location(module_path, "scrapers/"+module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if df is None:
            df = module.get_items()
        else:
            df = pd.concat([df, module.get_items()], ignore_index=True)
    items_req = [c for c in categories if isinstance(c, Item)]
    categories = [c for c in categories if isinstance(c, Category)]
    for item in lookup_filters:
        if lookup_filters[item][Category.NONE] in categories:
            items_req.append(item)
    items_req = set(items_req)
    items_df = set(df["name"])
    missing_items = list(items_req - items_df)
    if len(missing_items) > 0:
        raise Exception(f"Items {missing_items} are not scraped by {country}!")