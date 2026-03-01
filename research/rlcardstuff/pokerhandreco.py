import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from collections import Counter
from sklearn.preprocessing import LabelEncoder

# Load dataset from a CSV file
# Replace 'path_to_your_csv_file.csv' with the actual path to your CSV file
data = pd.read_excel("/Users/vishrutgrover/coding/pokerai/pokersomething/poker_dataset_processed.xls")

def is_straight(ranks):
    """Check if the hand is a straight."""
    if len(set(ranks)) != 5:
        return False
    return max(ranks) - min(ranks) == 4

def is_flush(suits):
    """Check if the hand is a flush."""
    return len(set(suits)) == 1

def hand_rank(suits, ranks):
    """Determine the rank of a poker hand."""
    count = Counter(ranks)
    unique_ranks = set(ranks)
    sorted_ranks = sorted(unique_ranks, reverse=True)

    if is_straight(ranks) and is_flush(suits):
        return 'Straight Flush'
    elif 4 in count.values():
        return 'Four of a Kind'
    elif sorted(count.values(), reverse=True) == [3, 2]:
        return 'Full House'
    elif is_flush(suits):
        return 'Flush'
    elif is_straight(ranks):
        return 'Straight'
    elif 3 in count.values():
        return 'Three of a Kind'
    elif list(count.values()).count(2) == 2:
        return 'Two Pair'
    elif 2 in count.values():
        return 'One Pair'
    else:
        return 'High Card'

def evaluate_hand(row):
    suits = [row[f'S{i}'] for i in range(1, 8)]
    ranks = [row[f'C{i}'] for i in range(1, 8)]
    return hand_rank(suits, ranks)

# Apply the hand evaluation function to create the 'HandRank' column
data['HandRank'] = data.apply(evaluate_hand, axis=1)

# Encode the hand ranks into numerical labels
label_encoder = LabelEncoder()
data['HandRank'] = label_encoder.fit_transform(data['HandRank'])


# Split data into features and labels
X = data.iloc[:, :-1].values  # All columns except 'HandRank'
y = data['HandRank'].values

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Convert arrays to PyTorch tensors
X_train_tensor = torch.tensor(X_train, dtype=torch.float)
X_test_tensor = torch.tensor(X_test, dtype=torch.float)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)

# Create TensorDatasets and DataLoaders
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)

batch_size = 64
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)


# Define the MLP model
class MLP(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out


# Model instantiation
input_size = X_train.shape[1]
hidden_size = 100  # Example hidden size
num_classes = len(torch.unique(y_train_tensor))
model = MLP(input_size, hidden_size, num_classes)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training the model
# Training the model
num_epochs = 10
for epoch in range(num_epochs):
    for i, (features, labels) in enumerate(train_loader):
        # Forward pass
        outputs = model(features)
        loss = criterion(outputs, labels)

        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (i + 1) % 100 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Step [{i + 1}/{len(train_loader)}], Loss: {loss.item():.4f}')