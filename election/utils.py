import tempfile
import matplotlib.pyplot as plt


def generate_chart(names, votes):
    """
    Generates a bar chart representing the vote results.

    Parameters
    ----------
    names : list
        List of candidate names.
    votes : list
        List of corresponding vote counts for each candidate.

    Returns
    -------
    str
        File path to the generated chart image.

    Notes
    -----
    This function generates a bar chart using Matplotlib library based on the provided
    candidate names and their corresponding vote counts. The chart is saved as a PNG
    image file in a temporary location, and the file path is returned.
    """
    plt.bar(names, votes)
    plt.xlabel('Candidates')
    plt.ylabel('Votes')
    plt.title('Vote Results')

    _, temp_file = tempfile.mkstemp(suffix='.png')
    plt.savefig(temp_file, format='png')
    plt.close()

    return temp_file
