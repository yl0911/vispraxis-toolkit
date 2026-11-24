"""Select historical ByteAI outdoor classes and paired images."""
from pathlib import Path
from scripts.datasets.select_voc_samples_by_labels import run
BASE=Path(r"E:\yl\data\resources\byteai_train_all");OUTPUT=BASE.parent/"byteai_outdoor_selected"
CLASSES={"BALANCE","BICYCLE","CHAIR","CLEANING_CAR","ELECTROMOBILE","FLOWER_CART","FRUIT_BASKET","FRUIT_CART","GAME_PLAYER","GAS","HUMAN","LAW_CAR","MEAT_CART","PLANT","PLAY_GROUND","POTATO_CART","REST_CHAIR","TABLE_LONG","TABLE_ROUND","TOYS","TRICYCLE","TRUCK","VEGETABLE_CART","VEHICLE","ADVERTISEMENT","TRASH_CAN","TRASH_CAN_FULL","UMBRELLA","NORMAL_CART","OTHER_CART"}
def main()->int:
    try:r=run(BASE,BASE,OUTPUT,include=CLASSES)
    except Exception as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())
