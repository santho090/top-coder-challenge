#!/usr/bin/env python3
"""
Final Legacy Reimbursement Calculator
Combines decision tree with special handling for extreme cases

Key insight: Very high receipts (>$1800) seem to have severe caps
that the decision tree doesn't capture well.
"""

import sys
sys.path.append('src')
from generated_tree_calculator import calculate_reimbursement_tree

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Final calculator with extreme case handling
    
    Args:
        trip_duration_days (int): Number of days traveling
        miles_traveled (float): Total miles traveled (can be decimal)
        total_receipts_amount (float): Total receipt amount
        
    Returns:
        float: Calculated reimbursement amount (rounded to 2 decimal places)
    """
    days = trip_duration_days
    miles = miles_traveled
    receipts = total_receipts_amount
    
    # Get base prediction from decision tree
    base_prediction = calculate_reimbursement_tree(days, miles, receipts)
    
    # Apply extreme case adjustments
    
    # Extreme high receipt penalty
    if receipts > 1800:
        # Very high receipts seem to have severe diminishing returns
        penalty_factor = min(0.6, 1800 / receipts)  # Cap at 60% of tree prediction
        base_prediction *= penalty_factor
        
        # Additional flat penalty for extreme cases
        if receipts > 2000:
            base_prediction -= 100
            
    elif receipts > 1400:
        # High receipts have moderate penalty
        penalty_factor = 0.8
        base_prediction *= penalty_factor
        
    # Extreme high mileage penalty (for cases like 1082 miles in 1 day)
    efficiency = miles / days if days > 0 else 0
    if efficiency > 800:  # More than 800 miles per day is extreme
        extreme_penalty = (efficiency - 800) * 0.5
        base_prediction -= extreme_penalty
        
    # Very low receipt bonus (cases with <$10 receipts seem to get higher rates)
    if receipts < 10:
        low_receipt_bonus = (10 - receipts) * 5
        base_prediction += low_receipt_bonus
        
    # Ensure minimum reimbursement
    if base_prediction < 50:
        base_prediction = 50
        
    return round(base_prediction, 2)

def calculate_reimbursement_conservative(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    More conservative approach for extreme cases
    """
    days = trip_duration_days
    miles = miles_traveled
    receipts = total_receipts_amount
    
    # Get base prediction
    base_prediction = calculate_reimbursement_tree(days, miles, receipts)
    
    # For the worst cases, apply more aggressive caps
    if receipts > 2000:
        # Extreme cases: cap at much lower value
        max_allowed = 200 + days * 50 + min(miles * 0.2, 200) + min(receipts * 0.1, 200)
        base_prediction = min(base_prediction, max_allowed)
        
    elif receipts > 1500:
        # High cases: moderate cap
        max_allowed = 300 + days * 60 + min(miles * 0.3, 300) + min(receipts * 0.2, 300)
        base_prediction = min(base_prediction, max_allowed)
        
    return round(base_prediction, 2)

def calculate_reimbursement_final(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Final ensemble approach
    """
    # Get predictions from both approaches
    pred1 = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
    pred2 = calculate_reimbursement_conservative(trip_duration_days, miles_traveled, total_receipts_amount)
    
    # Use conservative approach for extreme cases
    if total_receipts_amount > 1800:
        return pred2
    else:
        # Weighted average for normal cases
        return round(0.7 * pred1 + 0.3 * pred2, 2)

if __name__ == "__main__":
    # Test with the worst cases
    worst_cases = [
        (4, 69, 2321.49, 322.00),      # Case 152
        (1, 1082, 1809.49, 446.94),   # Case 996  
        (8, 795, 1645.99, 644.69),    # Case 684
        (5, 516, 1878.49, 669.85),    # Case 711
        (3, 93, 1.42, 364.51),        # Normal case for comparison
    ]
    
    for days, miles, receipts, expected in worst_cases:
        tree_pred = calculate_reimbursement_tree(days, miles, receipts)
        final_pred = calculate_reimbursement_final(days, miles, receipts)
        
        tree_error = abs(tree_pred - expected)
        final_error = abs(final_pred - expected)
        
        improvement = "✅" if final_error < tree_error else "❌"
        
        print(f"Case {days}d, {miles}mi, ${receipts}:")
        print(f"  Expected: ${expected}")
        print(f"  Tree: ${tree_pred} (error: ${tree_error:.2f})")
        print(f"  Final: ${final_pred} (error: ${final_error:.2f}) {improvement}")
        print() 