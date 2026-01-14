from helpers.quantity_norm import NormalizedQuantity

if __name__ == "__main__":
    norm_repo = NormalizedQuantity()

    normalize_quantity = norm_repo.get_normalized_quantity(
        algoname= "DRB_N",
        clientID= "B1700057",
        original_quantity= 150
    )

    print(type(normalize_quantity))