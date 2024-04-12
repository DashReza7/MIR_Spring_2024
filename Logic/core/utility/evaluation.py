from typing import List
import wandb
import numpy as np

class Evaluation:

    def __init__(self, name: str):
            self.name = name

    def calculate_precision(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the precision of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The precision of the predicted results
        """
        tp = 0
        total = 0
        for i in range(len(actual)):
            tp += len(set(actual[i]).intersection(set(predicted[i]))) 
            total += len(set(predicted[i])) 
        return tp / total
    
    def calculate_recall(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the recall of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The recall of the predicted results
        """
        tp = 0
        total = 0
        for i in range(len(actual)):
            tp += len(set(actual[i]).intersection(set(predicted[i]))) 
            total += len(set(actual[i])) 
        return tp / total  
    
    def calculate_F1(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the F1 score of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The F1 score of the predicted results    
        """
        p = self.calculate_precision(actual=actual, predicted=predicted)
        r = self.calculate_recall(actual=actual, predicted=predicted)
        f1 = 0.0
        if p == 0 and r == 0:
            f1 = 0
        else:
            f1 = (2 * p * r) / (p + r)
        return f1
    
    def calculate_AP(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Mean Average Precision of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The Average Precision of the predicted results
        """
        AP = 0.0
        tp = 0
        for i in range(len(predicted)):
            if predicted[i] in actual:
                tp += 1
                AP += tp / (i+1)
        return AP / tp
    
    def calculate_MAP(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Mean Average Precision of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The Mean Average Precision of the predicted results
        """
        MAP = 0.0
        for i in range(len(predicted)):
            MAP += self.calculate_AP(actual[i], predicted[i])
        return MAP / len(predicted)
    
    def cacluate_DCG(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Normalized Discounted Cumulative Gain (NDCG) of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The DCG of the predicted results
        """
        DCG = 0.0
        N = len(predicted)
        for i in range(N):
            for j in range(len(predicted[i])):
                if predicted[i][j] in actual[i]:
                    if j == 0:
                        DCG += len(actual[i]) - actual[i].index(predicted[i][j])
                    else:
                        DCG += (len(actual[i]) - actual[i].index(predicted[i][j])) / (np.log(j + 1))
        return DCG / N
    
    def cacluate_NDCG(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Normalized Discounted Cumulative Gain (NDCG) of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The NDCG of the predicted results
        """
        NDCG = 0.0
        N = len(predicted)
        for i in range(N):
            normal_coeffs = []
            for j in range(len(actual[i])):
                if j == 0:
                    normal_coeffs.append(len(actual[i]))
                else:
                    normal_coeffs.append(normal_coeffs[-1] + (len(actual[i]) - j) / (np.log(j + 1)))
            for j in range(len(predicted[i])):
                if predicted[i][j] in actual[i]:
                    if j == 0:
                        NDCG += (len(actual[i]) - actual[i].index(predicted[i][j])) / len(actual[i])
                    else:    
                        NDCG += ((len(actual[i]) - actual[i].index(predicted[i][j])) / (np.log(j + 1))) / normal_coeffs[j]
        return NDCG
    
    def cacluate_RR(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Mean Reciprocal Rank of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The Reciprocal Rank of the predicted results
        """
        for i in range(len(predicted)):
            if predicted[i] in actual:
                    return 1 / (i + 1)
    
    def cacluate_MRR(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Mean Reciprocal Rank of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The MRR of the predicted results
        """
        MRR = 0.0
        for i in range(len(predicted)):
            MRR += self.cacluate_RR(actual[i], predicted[i])
        return MRR / len(predicted)

    def print_evaluation(self, precision, recall, f1, ap, MAP, dcg, ndcg, rr, mrr):
        """
        Prints the evaluation metrics

        parameters
        ----------
        precision : float
            The precision of the predicted results
        recall : float
            The recall of the predicted results
        f1 : float
            The F1 score of the predicted results
        ap : float
            The Average Precision of the predicted results
        map : float
            The Mean Average Precision of the predicted results
        dcg: float
            The Discounted Cumulative Gain of the predicted results
        ndcg : float
            The Normalized Discounted Cumulative Gain of the predicted results
        rr: float
            The Reciprocal Rank of the predicted results
        mrr : float
            The Mean Reciprocal Rank of the predicted results
            
        """
        print(f"name = {self.name}\n")
        print(f'precision = {precision}')
        print(f'recall = {recall}')
        print(f'f1 = {f1}')
        print(f'ap = {ap}')
        print(f'map = {MAP}')
        print(f'dcg = {dcg}')
        print(f'ndcg = {ndcg}')
        print(f'rr = {rr}')
        print(f'mrr = {mrr}')
      
    def log_evaluation(self, precision, recall, f1, ap, map, dcg, ndcg, rr, mrr):
        """
        Use Wandb to log the evaluation metrics
      
        parameters
        ----------
        precision : float
            The precision of the predicted results
        recall : float
            The recall of the predicted results
        f1 : float
            The F1 score of the predicted results
        ap : float
            The Average Precision of the predicted results
        map : float
            The Mean Average Precision of the predicted results
        dcg: float
            The Discounted Cumulative Gain of the predicted results
        ndcg : float
            The Normalized Discounted Cumulative Gain of the predicted results
        rr: float
            The Reciprocal Rank of the predicted results
        mrr : float
            The Mean Reciprocal Rank of the predicted results
            
        """        
        wandb.init(project="Evaluation")
        wandb.log({"Precision": precision, "Recall": recall, "F1": f1, "MAP": map, "DCG": dcg, "NDCG": ndcg, "MRR": mrr})

    def calculate_evaluation(self, actual: List[List[str]], predicted: List[List[str]]):
        """
        call all functions to calculate evaluation metrics

        parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results
            
        """

        precision = self.calculate_precision(actual, predicted)
        recall = self.calculate_recall(actual, predicted)
        f1 = self.calculate_F1(actual, predicted)
        ap = self.calculate_AP(actual, predicted)
        map_score = self.calculate_MAP(actual, predicted)
        dcg = self.cacluate_DCG(actual, predicted)
        ndcg = self.cacluate_NDCG(actual, predicted)
        rr = self.cacluate_RR(actual, predicted)
        mrr = self.cacluate_MRR(actual, predicted)

        #call print and viualize functions
        self.print_evaluation(precision, recall, f1, ap, map_score, dcg, ndcg, rr, mrr)
        self.log_evaluation(precision, recall, f1, ap, map_score, dcg, ndcg, rr, mrr)
