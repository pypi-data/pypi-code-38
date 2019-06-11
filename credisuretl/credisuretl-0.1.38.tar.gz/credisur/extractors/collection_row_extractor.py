from credisur.models import Collection

def collection_row_extractor(results, unpacker):
    document = unpacker.get_value_at(2)
    raw_code = unpacker.get_value_at(5) or ""
    date = unpacker.get_value_at(1)
    customer = unpacker.get_value_at(3)
    amount = unpacker.get_value_at(4)

    collection = Collection(document, raw_code,
                            customer,
                            date, amount,
                            results.get_errors())

    results.append_to_collections(collection)
    results.append_to_collections_for_customers(customer, collection)