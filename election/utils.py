import tempfile
import matplotlib.pyplot as plt


def generate_chart(names, votes):
    plt.bar(names, votes)
    plt.xlabel('Candidates')
    plt.ylabel('Votes')
    plt.title('Vote Results')

    _, temp_file = tempfile.mkstemp(suffix='.png')
    plt.savefig(temp_file, format='png')
    plt.close()

    return temp_file
