package com.stc.labs.customer.domain.model;

import org.springframework.data.cassandra.core.mapping.PrimaryKey;
import org.springframework.data.cassandra.core.mapping.Table;

@Table
public class Customer {
	
	@PrimaryKey
	private int customerId;
	private String customerName;
	private String customerPhone;
	private String customerType;
	private String customerSubType;
		
	public Customer(){}
	
	
	/**
	 * @param customerId
	 * @param customerName
	 * @param customerPhone
	 * @param customerType
	 * @param customerSubType
	 */
	public Customer(int customerId, String customerName, String customerPhone, String customerType,
			String customerSubType) {
		super();
		this.customerId = customerId;
		this.customerName = customerName;
		this.customerPhone = customerPhone;
		this.customerType = customerType;
		this.customerSubType = customerSubType;
	}




	public int getCustomerId() {
		return customerId;
	}




	public void setCustomerId(int customerId) {
		this.customerId = customerId;
	}




	public String getCustomerName() {
		return customerName;
	}




	public void setCustomerName(String customerName) {
		this.customerName = customerName;
	}




	public String getCustomerPhone() {
		return customerPhone;
	}




	public void setCustomerPhone(String customerPhone) {
		this.customerPhone = customerPhone;
	}




	public String getCustomerType() {
		return customerType;
	}




	public void setCustomerType(String customerType) {
		this.customerType = customerType;
	}




	public String getCustomerSubType() {
		return customerSubType;
	}




	public void setCustomerSubType(String customerSubType) {
		this.customerSubType = customerSubType;
	}




	@Override
	public String toString() {
		return String.format("Customer[customerId=%d, customerName='%s', customerPhone='%s', customerType='%s, customerSubType='%s'']", this.customerId,
				this.customerName, this.customerPhone, this.customerType, this.customerSubType);
	}
}