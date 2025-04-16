from DeepPurpose.utils import *
from DeepPurpose.dataset import *
from DeepPurpose import utils, dataset
from DeepPurpose import DTI as models
import warnings
warnings.filterwarnings("ignore")
import sklearn as sk


X_drugs, X_targets, y = dataset.load_process_DAVIS(path = './data', binary = False, convert_to_log = True, threshold = 30)
print('Drug 1: ' + X_drugs[0])
print('Target 1: ' + X_targets[0])
print('Score 1: ' + str(y[0]))

drug_encoding, target_encoding = 'MPNN', 'CNN'

#split data into training, validation and testing
train, val, test = utils.data_process(X_drugs, X_targets, y, 
                                drug_encoding, target_encoding, 
                                split_method='random',frac=[0.7,0.1,0.2],
                                random_seed = 1)

# load my trained model 
model = models.model_pretrained('models/my_trained_model/')
#model testing
y_pred = model.predict(test)

#Calculate mean squared error regression loss.
mse = sk.metrics.mean_squared_error(test['Label'], y_pred)
print('The mean square error for test set ' + str(mse))