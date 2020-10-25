import argparse
from torch import cuda

UNK_token = 0
PAD_token = 1
SOS_token = 2
EOS_token = 3
ENT_token = 4

MAX_GPU_SAMPLES = 4


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment_ID", type=str, default="")
    parser.add_argument("-bs", "--batch_size", type=int,
                        default=MAX_GPU_SAMPLES)
    parser.add_argument("--MAX_GPU_SAMPLES", type=int, default=MAX_GPU_SAMPLES)
    parser.add_argument("--parallel_decode", type=bool, default=True)
    parser.add_argument("--hidden", type=int, default=400)
    parser.add_argument("-lr", "--learning_rate", type=float, default=0.001)
    parser.add_argument("-dr", "--dropout", type=float, default=0.2)
    parser.add_argument('-clip', '--clip', help='gradient clipping',
                        default=10, type=int)
    parser.add_argument('-tfr', '--teacher_forcing_ratio',
                        help='teacher_forcing_ratio', type=float, default=0.5)
    parser.add_argument('--load_embedding', type=bool, default=True)
    parser.add_argument('--model_path', type=str,
                        help="Use model_path if you want to load a pre-trained model")
    parser.add_argument('--lang_path', type=str, default="lang_data")
    parser.add_argument('--log_path', type=str)
    parser.add_argument('--dataset', type=str, default='multiwoz')
    parser.add_argument('--task', type=str, default='DST')
    parser.add_argument('--patience', type=int, default=6)
    parser.add_argument('--eval_patience', type=int, default=1)
    parser.add_argument('--gen_sample', action='store_true')
    parser.add_argument('--train_data_ratio', type=int, default=100)
    parser.add_argument('--dev_data_ratio', type=int, default=100)
    parser.add_argument('--test_data_ratio', type=int, default=100)
    parser.add_argument('--ground_truth_labels', action="store_true")
    parser.add_argument('--NER_labels', action="store_true")

    args = parser.parse_args()

    assert(not (args.ground_truth_labels and args.NER_labels)), "Select only one of either ground truth, or NER labels"

    setattr(args, 'device', 'cuda' if cuda.is_available() else 'cpu')
    setattr(args, 'UNK_token', 0)
    setattr(args, 'PAD_token', 1)
    setattr(args, 'SOS_token', 2)
    setattr(args, 'EOS_token', 3)
    setattr(args, 'ENT_token', 4)
    setattr(args, 'unk_mask', True)
    setattr(args, 'early_stopping', None)

    return vars(args)