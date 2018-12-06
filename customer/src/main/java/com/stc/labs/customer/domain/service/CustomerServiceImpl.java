package com.stc.labs.customer.domain.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;

import com.stc.labs.customer.domain.model.Customer;
import com.stc.labs.customer.repo.CustomerRepository;

public class CustomerServiceImpl implements CustomerService {

	@Autowired
	CustomerRepository customerRepository;
	
	@Override
	public List<Customer> findByCustomerPhone(String customerPhone) {		
		return customerRepository.findByCustomerPhone(customerPhone); 
	}

	@Override
	public List<Customer> findByCustomerId(int customerId) {
		return customerRepository.findByCustomerId(customerId);
	}

}
