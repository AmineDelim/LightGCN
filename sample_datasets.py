import os
import random
import argparse

random.seed(42)

def sample_dataset(dataset_name, user_ratio=0.1):
    src_path = os.path.join("Data_original", dataset_name)
    dst_path = os.path.join("Data", dataset_name)

    os.makedirs(dst_path, exist_ok=True)

    def read_file(path):
        data = {}
        with open(path) as f:
            for line in f:
                tokens = line.strip().split()
                if len(tokens) < 2:
                    continue
                uid = int(tokens[0])
                items = list(map(int, tokens[1:]))
                data[uid] = items
        return data

    train_data = read_file(os.path.join(src_path, "train.txt"))
    test_data  = read_file(os.path.join(src_path, "test.txt"))

    common_users = list(set(train_data.keys()) & set(test_data.keys()))
    print(f"[{dataset_name}] "
          f"train_users={len(train_data)}, test_users={len(test_data)}, "
          f"common_users={len(common_users)}")

    n_sample = max(1, min(int(len(common_users) * user_ratio), len(common_users)))
    sampled_users = sorted(random.sample(common_users, n_sample))

    user_remap = {old: new for new, old in enumerate(sampled_users)}

    all_items = set()
    for uid in sampled_users:
        all_items.update(train_data[uid])
        all_items.update(test_data[uid])
    item_remap = {old: new for new, old in enumerate(sorted(all_items))}

    with open(os.path.join(dst_path, "train.txt"), "w") as f:
        for old_uid in sampled_users:
            new_uid = user_remap[old_uid]
            new_items = [item_remap[i] for i in train_data[old_uid]]
            f.write(f"{new_uid} {' '.join(map(str, new_items))}\n")

    with open(os.path.join(dst_path, "test.txt"), "w") as f:
        for old_uid in sampled_users:
            new_uid = user_remap[old_uid]
            new_items = [item_remap[i] for i in test_data[old_uid]]
            f.write(f"{new_uid} {' '.join(map(str, new_items))}\n")

    with open(os.path.join(dst_path, "user_list.txt"), "w") as f:
        f.write("org_id remap_id\n")
        for old_uid, new_uid in user_remap.items():
            f.write(f"{old_uid} {new_uid}\n")

    with open(os.path.join(dst_path, "item_list.txt"), "w") as f:
        f.write("org_id remap_id\n")
        for old_item, new_item in item_remap.items():
            f.write(f"{old_item} {new_item}\n")

    print(f"[{dataset_name}] "
          f"{len(sampled_users)} users, {len(all_items)} items → done")


ALL_DATASETS = ["gowalla", "yelp2018", "amazon-book"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratio", type=float, default=0.1,
                        help="Fraction of users to keep (default: 0.1 = 10%%)")
    parser.add_argument("--dataset", type=str, default="all",
                        choices=ALL_DATASETS + ["all"],
                        help="Dataset to sample: gowalla | yelp2018 | amazon-book | all (default: all)")
    args = parser.parse_args()

    targets = ALL_DATASETS if args.dataset == "all" else [args.dataset]

    for ds in targets:
        if not os.path.exists(os.path.join("Data_original", ds)):
            print(f"[SKIP] Data_original/{ds} not found")
            continue
        sample_dataset(ds, user_ratio=args.ratio)
