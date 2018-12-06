package com.stc.labs.customer.domain.service;

import java.util.List;

import com.stc.labs.customer.domain.model.Customer;

public interface CustomerService {
	
	public List<Customer> findByCustomerPhone(String customerPhone);
	public List<Customer> findByCustomerId(int customerId);	

}
