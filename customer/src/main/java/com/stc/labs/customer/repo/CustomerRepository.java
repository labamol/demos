package com.stc.labs.customer.repo;

import java.util.List;

import org.springframework.data.cassandra.repository.AllowFiltering;
import org.springframework.data.cassandra.repository.CassandraRepository;
import org.springframework.data.cassandra.repository.Query;
import org.springframework.data.repository.CrudRepository;
 
import com.stc.labs.customer.domain.model.Customer;

/**
public interface CustomerRepository extends CrudRepository<Customer, String> {
	
	@Query(value="SELECT * FROM customer WHERE customerPhone=?0")
	public List<Customer> findByCustomerPhone(String customerPhone);
 
	@Query(value="SELECT * FROM customer WHERE customerId=?0")
	public List<Customer> findByCustomerId(int customerId);	
}	

**/

public interface CustomerRepository extends CassandraRepository<Customer, String> {
	 
	@AllowFiltering
	public List<Customer> findByCustomerPhone(String customerPhone);
 
	@AllowFiltering
	public List<Customer> findByCustomerId(int customerId);
}

