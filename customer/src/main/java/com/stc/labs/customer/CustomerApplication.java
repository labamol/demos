package com.stc.labs.customer;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import com.stc.labs.customer.domain.model.Customer;
import com.stc.labs.customer.repo.CustomerRepository;

@SpringBootApplication
public class CustomerApplication {

	@Autowired
    CustomerRepository customerRepository;
	
	public static void main(String[] args) {
		SpringApplication.run(CustomerApplication.class, args);
	
	}
	
	public void run(String[] args) throws Exception {
			clearData();
			saveData();
			lookup();
		}
		
		public void clearData(){
			customerRepository.deleteAll();
		}
		
		public void saveData(){
			System.out.println("===================Save Customers to Cassandra===================");
			Customer cust_1 = new Customer(1, "PeterSmith", "9008397190", "A", "A2");
	        Customer cust_2 = new Customer(2, "MaryTaylor", "9008397191", "B", "B1");
	        Customer cust_3 = new Customer(3, "PeterBrown", "7398397190", "C", "C3");
	        Customer cust_4 = new Customer(4, "LaurenTaylor", "9073797190", "A", "A1");
	        Customer cust_5 = new Customer(5, "LaurenFlores", "7808397190", "B", "B1");
	        Customer cust_6 = new Customer(6, "PeterWilliams", "8908397190", "C", "C2");
	 
	        // save customers to ElasticSearch
	        customerRepository.save(cust_1);
	        customerRepository.save(cust_2);
	        customerRepository.save(cust_3);
	        customerRepository.save(cust_4);
	        customerRepository.save(cust_5);
	        customerRepository.save(cust_6);
		}
		
		public void lookup(){
			System.out.println("===================Lookup Customers from Cassandra by id===================");
			List<Customer> customers1 = customerRepository.findByCustomerId(1);
			customers1.forEach(System.out::println);
	 
			System.out.println("===================Lookup Customers from Cassandra by phone===================");
			List<Customer> customers2 = customerRepository.findByCustomerPhone("9008397190");
			customers2.forEach(System.out::println);
		}
	
		
		
		
	}
