def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', type=str)
    return parser.parse_args()

def main():
    param = get_args()

if __name__ == '__main__':
    main()