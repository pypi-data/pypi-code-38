from add_ints import create_network


def main():
    network = create_network()
    
    print('='*80)
    print('\n\n')

    print(network.parent.dumps('json', indent=2))
    print('\n\n')

    print('='*80)
    print('\n\n')

    print(network.parent.dumps('yaml'))

    print('\n\n')
    print('='*80)

if __name__ == '__main__':
    main()
