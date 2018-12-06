package com.stc.labs.customer.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.stc.labs.customer.domain.model.Customer;
import com.stc.labs.customer.domain.service.CustomerService;



@RestController
public class CustomerController {

	@Autowired
    private CustomerService service;

    @RequestMapping(method = RequestMethod.GET, produces = "application/json")
    public List<Customer> findByCustomerId(@RequestParam(value="customerId") int customerId) {
      return service.findByCustomerId(customerId);
    } 

    @RequestMapping(method = RequestMethod.GET, produces = "application/json")
    public List<Customer> findByCustomerPhone(@RequestParam(value="customerPhone") String customerPhone) {
      return service.findByCustomerPhone(customerPhone);
    } 
	
}
