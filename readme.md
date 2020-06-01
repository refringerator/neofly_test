
# Веб-приложение на django - Система бронирования заказов для аэродинамического комплекса
## Введение
Существет информационная система аэродинамического комплекса, в которой предусмотрен ввод всевозможных операций, от бронирования полетов, продажи сертификатов и прочее. Чтобы расширить функционал системы и интегрировать онлайн продажи было разработано API.

### Порядок взаимодействия
Все значимые операции проверяются через API ИС комплекса. 
<details><summary>Описание веб-сервера на wsdl (открывается по клику)</summary>
<p>

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
		xmlns:soap12bind="http://schemas.xmlsoap.org/wsdl/soap12/"
		xmlns:soapbind="http://schemas.xmlsoap.org/wsdl/soap/"
		xmlns:tns="neo-fly"
		xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy"
		xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		xmlns:xsd1="neo-fly"
		name="Neofly"
		targetNamespace="neo-fly">
	<types>
		<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
				xmlns:xs1="neo-fly"
				targetNamespace="neo-fly"
				attributeFormDefault="unqualified"
				elementFormDefault="qualified">
			<xs:element name="record">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="tariffId"
								type="xs:string"/>
						<xs:element name="minutes"
								type="xs:integer"/>
						<xs:element name="sum"
								type="xs:decimal"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="certificate">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="number"
								type="xs:string"/>
						<xs:element name="certificateType"
								type="xs:string"/>
						<xs:element name="flightTime"
								type="xs:integer"/>
						<xs:element name="status"
								type="xs:integer"
								minOccurs="0"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="availableElement">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="startDate"
								type="xs:dateTime"/>
						<xs:element name="minutesAvailable"
								type="xs:integer"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="detail">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="from"
								type="xs:integer"/>
						<xs:element name="to"
								type="xs:integer"/>
						<xs:element name="price"
								type="xs:decimal"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="availableTariff">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="tariffId"
								type="xs:string"/>
						<xs:element name="name"
								type="xs:string"/>
						<xs:element name="step"
								type="xs:integer"/>
						<xs:element name="minTime"
								type="xs:integer"/>
						<xs:element name="tariffDetails">
							<xs:complexType>
								<xs:sequence>
									<xs:element ref="tns:detail"
											minOccurs="0"
											maxOccurs="unbounded"/>
								</xs:sequence>
							</xs:complexType>
						</xs:element>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="newCertificate">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="certificateType"
								type="xs:string"/>
						<xs:element name="flightTime"
								type="xs:integer"/>
						<xs:element name="price"
								type="xs:decimal"/>
						<xs:element name="count"
								type="xs:integer"
								minOccurs="0"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="availableCertificate">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="certificateType"
								type="xs:string"/>
						<xs:element name="flightTime"
								type="xs:integer"/>
						<xs:element name="price"
								type="xs:decimal"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:complexType name="AvailableCertificateResponse">
				<xs:sequence>
					<xs:element name="status"
							type="xs:integer"/>
					<xs:element name="description"
							type="xs:string"
							minOccurs="0"/>
					<xs:element name="certificates"
							minOccurs="0">
						<xs:complexType>
							<xs:sequence>
								<xs:element ref="tns:availableCertificate"
										minOccurs="0"
										maxOccurs="unbounded"/>
							</xs:sequence>
						</xs:complexType>
					</xs:element>
				</xs:sequence>
			</xs:complexType>
			<xs:complexType name="CheckCertificateResponseType">
				<xs:sequence>
					<xs:element ref="tns:certificate"/>
					<xs:element name="status"
							type="xs:integer"/>
					<xs:element name="description"
							type="xs:string"
							minOccurs="0"/>
				</xs:sequence>
			</xs:complexType>
			<xs:complexType name="FllightTimeType">
				<xs:sequence>
					<xs:element name="tariffRecords"
							minOccurs="0">
						<xs:complexType>
							<xs:sequence>
								<xs:element ref="tns:record"
										minOccurs="0"
										maxOccurs="unbounded"/>
							</xs:sequence>
						</xs:complexType>
					</xs:element>
					<xs:element name="certificates"
							minOccurs="0">
						<xs:complexType>
							<xs:sequence>
								<xs:element ref="tns:certificate"
										minOccurs="0"
										maxOccurs="unbounded"/>
							</xs:sequence>
						</xs:complexType>
					</xs:element>
					<xs:element name="depositMinutes"
							type="xs:integer"
							minOccurs="0"/>
				</xs:sequence>
			</xs:complexType>
			<xs:complexType name="OrderResponse">
				<xs:sequence>
					<xs:element name="status"
							type="xs:integer"/>
					<xs:element name="description"
							type="xs:string"
							minOccurs="0"/>
					<xs:element name="invoiceId"
							minOccurs="0"/>
				</xs:sequence>
			</xs:complexType>
			<xs:complexType name="UserInfoType">
				<xs:sequence>
					<xs:element name="UserId"
							type="xs:integer"/>
					<xs:element name="isDepositAvailable"
							type="xs:boolean"
							minOccurs="0"/>
					<xs:element name="minutesOnDeposit"
							type="xs:integer"
							minOccurs="0"/>
					<xs:element name="status"
							type="xs:integer"
							minOccurs="0"/>
					<xs:element name="description"
							type="xs:string"
							minOccurs="0"/>
				</xs:sequence>
			</xs:complexType>
			<xs:complexType name="availableTariffs">
				<xs:sequence>
					<xs:element name="SlotTime"
							type="xs:dateTime"/>
					<xs:element name="minutesAvailable"
							type="xs:integer"/>
					<xs:element name="Items">
						<xs:complexType>
							<xs:sequence>
								<xs:element ref="tns:availableTariff"
										minOccurs="0"
										maxOccurs="unbounded"/>
							</xs:sequence>
						</xs:complexType>
					</xs:element>
					<xs:element name="UserId"
							type="xs:integer"/>
				</xs:sequence>
			</xs:complexType>
			<xs:complexType name="availableTime">
				<xs:sequence>
					<xs:element name="PeriodType"
							type="xs:string"/>
					<xs:element name="ItemLenght"
							type="xs:integer"/>
					<xs:element name="Items">
						<xs:complexType>
							<xs:sequence>
								<xs:element ref="tns:availableElement"
										minOccurs="0"
										maxOccurs="unbounded"/>
							</xs:sequence>
						</xs:complexType>
					</xs:element>
					<xs:element name="UserId"
							type="xs:integer"/>
				</xs:sequence>
			</xs:complexType>
			<xs:complexType name="confirmOrderResponse">
				<xs:sequence>
					<xs:element name="status"
							type="xs:integer"/>
					<xs:element name="description"
							type="xs:string"
							minOccurs="0"/>
				</xs:sequence>
			</xs:complexType>
			<xs:complexType name="orderRequest">
				<xs:sequence>
					<xs:element name="flightTime"
							type="tns:FllightTimeType"
							minOccurs="0"/>
					<xs:element name="newCertificates"
							minOccurs="0">
						<xs:complexType>
							<xs:sequence>
								<xs:element ref="tns:newCertificate"
										maxOccurs="unbounded"/>
							</xs:sequence>
						</xs:complexType>
					</xs:element>
					<xs:element name="depositMinutes"
							type="xs:integer"
							minOccurs="0"/>
					<xs:element name="total"
							type="xs:decimal"/>
					<xs:element name="UserId"
							type="xs:integer"/>
				</xs:sequence>
			</xs:complexType>
			<xs:element name="getAvailableDates">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="Month"
								type="xs:dateTime"/>
						<xs:element name="UserId"
								type="xs:integer"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getAvailableDatesResponse">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="return"
								type="tns:availableTime"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getAvailableSlots">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="Date"
								type="xs:dateTime"/>
						<xs:element name="UserId"
								type="xs:integer"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getAvailableSlotsResponse">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="return"
								type="tns:availableTime"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getAvailableTariffs">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="SlotTime"
								type="xs:dateTime"/>
						<xs:element name="UserId"
								type="xs:integer"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getAvailableTariffsResponse">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="return"
								type="tns:availableTime"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="createOrder">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="Data"
								type="tns:orderRequest"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="createOrderResponse">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="return"
								type="tns:OrderResponse"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getUserInfo">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="UserId"
								type="xs:integer"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getUserInfoResponse">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="return"
								type="tns:UserInfoType"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="checkCertificate">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="certificateNumber"
								type="xs:string"/>
						<xs:element name="UserId"
								type="xs:integer"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="checkCertificateResponse">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="return"
								type="tns:CheckCertificateResponseType"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getAvailableCertificateTypes">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="UserId"
								type="xs:integer"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="getAvailableCertificateTypesResponse">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="return"
								type="tns:AvailableCertificateResponse"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="confirmOrder">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="invoiceId"
								type="xs:string"/>
						<xs:element name="transactionId"
								type="xs:string"
								nillable="true"/>
						<xs:element name="total"
								type="xs:string"
								nillable="true"/>
						<xs:element name="UserId"
								type="xs:integer"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="confirmOrderResponse">
				<xs:complexType>
					<xs:sequence>
						<xs:element name="return"
								type="tns:confirmOrderResponse"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
		</xs:schema>
	</types>
	<message name="getAvailableDatesRequestMessage">
		<part name="parameters"
				element="tns:getAvailableDates"/>
	</message>
	<message name="getAvailableDatesResponseMessage">
		<part name="parameters"
				element="tns:getAvailableDatesResponse"/>
	</message>
	<message name="getAvailableSlotsRequestMessage">
		<part name="parameters"
				element="tns:getAvailableSlots"/>
	</message>
	<message name="getAvailableSlotsResponseMessage">
		<part name="parameters"
				element="tns:getAvailableSlotsResponse"/>
	</message>
	<message name="getAvailableTariffsRequestMessage">
		<part name="parameters"
				element="tns:getAvailableTariffs"/>
	</message>
	<message name="getAvailableTariffsResponseMessage">
		<part name="parameters"
				element="tns:getAvailableTariffsResponse"/>
	</message>
	<message name="createOrderRequestMessage">
		<part name="parameters"
				element="tns:createOrder"/>
	</message>
	<message name="createOrderResponseMessage">
		<part name="parameters"
				element="tns:createOrderResponse"/>
	</message>
	<message name="getUserInfoRequestMessage">
		<part name="parameters"
				element="tns:getUserInfo"/>
	</message>
	<message name="getUserInfoResponseMessage">
		<part name="parameters"
				element="tns:getUserInfoResponse"/>
	</message>
	<message name="checkCertificateRequestMessage">
		<part name="parameters"
				element="tns:checkCertificate"/>
	</message>
	<message name="checkCertificateResponseMessage">
		<part name="parameters"
				element="tns:checkCertificateResponse"/>
	</message>
	<message name="getAvailableCertificateTypesRequestMessage">
		<part name="parameters"
				element="tns:getAvailableCertificateTypes"/>
	</message>
	<message name="getAvailableCertificateTypesResponseMessage">
		<part name="parameters"
				element="tns:getAvailableCertificateTypesResponse"/>
	</message>
	<message name="confirmOrderRequestMessage">
		<part name="parameters"
				element="tns:confirmOrder"/>
	</message>
	<message name="confirmOrderResponseMessage">
		<part name="parameters"
				element="tns:confirmOrderResponse"/>
	</message>
	<portType name="NeoflyPortType">
		<operation name="getAvailableDates">
			<input message="tns:getAvailableDatesRequestMessage"/>
			<output message="tns:getAvailableDatesResponseMessage"/>
		</operation>
		<operation name="getAvailableSlots">
			<input message="tns:getAvailableSlotsRequestMessage"/>
			<output message="tns:getAvailableSlotsResponseMessage"/>
		</operation>
		<operation name="getAvailableTariffs">
			<input message="tns:getAvailableTariffsRequestMessage"/>
			<output message="tns:getAvailableTariffsResponseMessage"/>
		</operation>
		<operation name="createOrder">
			<input message="tns:createOrderRequestMessage"/>
			<output message="tns:createOrderResponseMessage"/>
		</operation>
		<operation name="getUserInfo">
			<input message="tns:getUserInfoRequestMessage"/>
			<output message="tns:getUserInfoResponseMessage"/>
		</operation>
		<operation name="checkCertificate">
			<input message="tns:checkCertificateRequestMessage"/>
			<output message="tns:checkCertificateResponseMessage"/>
		</operation>
		<operation name="getAvailableCertificateTypes">
			<input message="tns:getAvailableCertificateTypesRequestMessage"/>
			<output message="tns:getAvailableCertificateTypesResponseMessage"/>
		</operation>
		<operation name="confirmOrder">
			<input message="tns:confirmOrderRequestMessage"/>
			<output message="tns:confirmOrderResponseMessage"/>
		</operation>
	</portType>
	<binding name="NeoflySoapBinding"
			type="tns:NeoflyPortType">
		<soapbind:binding style="document"
				transport="http://schemas.xmlsoap.org/soap/http"/>
		<operation name="getAvailableDates">
			<soapbind:operation style="document"
					soapAction="neo-fly#Neofly:getAvailableDates"/>
			<input>
				<soapbind:body use="literal"/>
			</input>
			<output>
				<soapbind:body use="literal"/>
			</output>
		</operation>
		<operation name="getAvailableSlots">
			<soapbind:operation style="document"
					soapAction="neo-fly#Neofly:getAvailableSlots"/>
			<input>
				<soapbind:body use="literal"/>
			</input>
			<output>
				<soapbind:body use="literal"/>
			</output>
		</operation>
		<operation name="getAvailableTariffs">
			<soapbind:operation style="document"
					soapAction="neo-fly#Neofly:getAvailableTariffs"/>
			<input>
				<soapbind:body use="literal"/>
			</input>
			<output>
				<soapbind:body use="literal"/>
			</output>
		</operation>
		<operation name="createOrder">
			<soapbind:operation style="document"
					soapAction="neo-fly#Neofly:createOrder"/>
			<input>
				<soapbind:body use="literal"/>
			</input>
			<output>
				<soapbind:body use="literal"/>
			</output>
		</operation>
		<operation name="getUserInfo">
			<soapbind:operation style="document"
					soapAction="neo-fly#Neofly:getUserInfo"/>
			<input>
				<soapbind:body use="literal"/>
			</input>
			<output>
				<soapbind:body use="literal"/>
			</output>
		</operation>
		<operation name="checkCertificate">
			<soapbind:operation style="document"
					soapAction="neo-fly#Neofly:checkCertificate"/>
			<input>
				<soapbind:body use="literal"/>
			</input>
			<output>
				<soapbind:body use="literal"/>
			</output>
		</operation>
		<operation name="getAvailableCertificateTypes">
			<soapbind:operation style="document"
					soapAction="neo-fly#Neofly:getAvailableCertificateTypes"/>
			<input>
				<soapbind:body use="literal"/>
			</input>
			<output>
				<soapbind:body use="literal"/>
			</output>
		</operation>
		<operation name="confirmOrder">
			<soapbind:operation style="document"
					soapAction="neo-fly#Neofly:confirmOrder"/>
			<input>
				<soapbind:body use="literal"/>
			</input>
			<output>
				<soapbind:body use="literal"/>
			</output>
		</operation>
	</binding>
	<binding name="NeoflySoap12Binding"
			type="tns:NeoflyPortType">
		<soap12bind:binding style="document"
				transport="http://schemas.xmlsoap.org/soap/http"/>
		<operation name="getAvailableDates">
			<soap12bind:operation style="document"
					soapAction="neo-fly#Neofly:getAvailableDates"/>
			<input>
				<soap12bind:body use="literal"/>
			</input>
			<output>
				<soap12bind:body use="literal"/>
			</output>
		</operation>
		<operation name="getAvailableSlots">
			<soap12bind:operation style="document"
					soapAction="neo-fly#Neofly:getAvailableSlots"/>
			<input>
				<soap12bind:body use="literal"/>
			</input>
			<output>
				<soap12bind:body use="literal"/>
			</output>
		</operation>
		<operation name="getAvailableTariffs">
			<soap12bind:operation style="document"
					soapAction="neo-fly#Neofly:getAvailableTariffs"/>
			<input>
				<soap12bind:body use="literal"/>
			</input>
			<output>
				<soap12bind:body use="literal"/>
			</output>
		</operation>
		<operation name="createOrder">
			<soap12bind:operation style="document"
					soapAction="neo-fly#Neofly:createOrder"/>
			<input>
				<soap12bind:body use="literal"/>
			</input>
			<output>
				<soap12bind:body use="literal"/>
			</output>
		</operation>
		<operation name="getUserInfo">
			<soap12bind:operation style="document"
					soapAction="neo-fly#Neofly:getUserInfo"/>
			<input>
				<soap12bind:body use="literal"/>
			</input>
			<output>
				<soap12bind:body use="literal"/>
			</output>
		</operation>
		<operation name="checkCertificate">
			<soap12bind:operation style="document"
					soapAction="neo-fly#Neofly:checkCertificate"/>
			<input>
				<soap12bind:body use="literal"/>
			</input>
			<output>
				<soap12bind:body use="literal"/>
			</output>
		</operation>
		<operation name="getAvailableCertificateTypes">
			<soap12bind:operation style="document"
					soapAction="neo-fly#Neofly:getAvailableCertificateTypes"/>
			<input>
				<soap12bind:body use="literal"/>
			</input>
			<output>
				<soap12bind:body use="literal"/>
			</output>
		</operation>
		<operation name="confirmOrder">
			<soap12bind:operation style="document"
					soapAction="neo-fly#Neofly:confirmOrder"/>
			<input>
				<soap12bind:body use="literal"/>
			</input>
			<output>
				<soap12bind:body use="literal"/>
			</output>
		</operation>
	</binding>
	<service name="Neofly">
		<port name="NeoflySoap"
				binding="tns:NeoflySoapBinding">
			<documentation> 
				<wsi:Claim xmlns:wsi="http://ws-i.org/schemas/conformanceClaim/"
						conformsTo="http://ws-i.org/profiles/basic/1.1"/>
			</documentation>
			<soapbind:address location="http://some.host/database/ws/neofly"/>
		</port>
		<port name="NeoflySoap12"
				binding="tns:NeoflySoap12Binding">
			<soap12bind:address location="http://some.host/database/ws/neofly"/>
		</port>
	</service>
</definitions>
```

</p>
</details>


Возможные операции веб-сервиса ИС:
1. getAvailableDates - Запрос списка дат, доступных для бронирования
2. getAvailableSlots - Запрос информации о временных интервалах, доступных для бронирования, а также времени, доступном для бронирования в каждом интервале
3. getAvailableTariffs - Запрос информации о тарифах на выбранную дату в выбранный интервал времени(доступные тарифы, стоимость в зависимости от продолжительности) и количестве доступных минут
4. createOrder - Загрузка данных заказа для проверки стоимости и получения идентификатора для отправки в платежную систему (если необходимо) 
5. confirmOrder - Подтверждение заказа (получение от платежной системы подтверждения оплаты или подтверждение ползователя на списание депозита/сертификата) 
5. getAvailableCertificateTypes - Запрос информации о доступных для приобретения категорий сертификатов, их номиналах и стоимости 
6. getUserInfo - Запрос информации по пользователю - статус клиента (в зависимости от статуса доступны различные опции), количество минут на депозите клиента
7. checkCertificate - Проверка сертификата по номеру, получение информации по сертификату - категория, полетное время, статус

## Что необходимо
Необходимо сделать базовую часть для проверки полноты доступных операций веб-сервиса, проверить веб-сервис на корректность работы, оценить время отклика.

В идеале сделать личный кабинет клиента с возможностью подтверждения номера телефона, бронирование полета и покупки подарочных сертификатов.
Продумать и реализовать алгоритм синхронизации пользователей.

## Используемые технологии
1. Django 3
    * django-debug-toolbar
    * djangorestframework
    * phone_login 
    * [Django-environ](https://django-environ.readthedocs.io/en/latest/#django-environ)
2. Nginx
3. Javascript, JQuery
4. Bootstrap 4
5. SOAP

## Что сделано
#### Изменена базовая модель пользователя
Для проекта встроеная пользовательская модель django не подходит, так как неободима идентификация пользователя по номеру телефона. На первый взгля для этих целей неплохо подошла
модель пользователя `phone_login/models.py #CustomUser(PhoneNumberUser)` основанная на абстрактной модели `PhoneNumberUser` из [django-phone-login](https://github.com/wejhink/django-phone-login). К тому же Django Phone Login позволяет логиниться и регистрироваться по номеру телефона. Не требует запоминания пароля от пользователей.
Добавляем в настройки приложения строку, чтобы использовать другую модель пользователя.
```
    AUTH_USER_MODEL = 'phone_login.CustomUser'
```

##### Порядок работы
1. Пользователь вводит `номер телефона` и отправляет запрос на генерацию `секретного кода`
2. `django-phone-login` отправляет `секретный код` в смс на телефон.
3. Пользователь отправляет `секретный код` на сервер для проверки.
4. `django-phone-login` проверяет `секретный код` и отправляет `токен` как ответ используя `DRF3`.

* https://docs.djangoproject.com/en/3.0/topics/auth/customizing/

#### Реализован вызов soap-сервиса информационной системы
Для вызова soap сервиса используется [Zeep: Python SOAP client](https://docs.python-zeep.org/en/master/)
Вызовы сервиса расположены в `booking/utils.py`

Сначала создаем объект клиент, указывая настройки подключения
```
def init_soap_client():
    session = Session()
    session.auth = HTTPBasicAuth(settings.WS_PROXY_LOGIN, settings.WS_PROXY_PASS)
    session.verify = not settings.WS_IGNORE_SSL

    client = zeep.Client(wsdl=settings.SOAP_WSDL,
                         wsse=UsernameToken(settings.WS_LOGIN, settings.WS_PASS),
                         transport=Transport(session=session))
    return client
```

Потом вызываем необходимый метод, для получения данных. Например, получение всех доступных дат в месяце
```
def get_available_dates(date_in_month, user_id):
    client = init_soap_client()
    res = client.service.getAvailableDates(Month=date_in_month, UserId=user_id)
    return res.Items
```

Вообще, SOAP основан на обмене XML-сообщениями. Хотя библиотека zeep и преобразовывает xml в объектное представлление, для отображения полученных данных на странице, их необходимо будет преобразовать.
Для этого написаны дополнительные функции, на второй остановимся чуть позже.
```
def available_dates_to_dict(dates):
    return {item.startDate: item.minutesAvailable for item in dates.availableElement}


def make_cert_table(certs):
    fl_time = []

    d = defaultdict(list)
    for cert_data in certs.availableCertificate:
        d[cert_data.certificateType].append({'flight_time': cert_data.flightTime,
                                             'price': cert_data.price,
                                             'disabled': ''
                                             })
        fl_time.append(cert_data.flightTime)

    fl_time.sort()
    head = set(fl_time)

    for key, value in d.items():
        fts = set([v['flight_time'] for v in value])
        for el in head - fts:
            d[key].append({'flight_time': el, 'price': '-', 'disabled': 'disabled'})

        d[key].sort(key=lambda element: element['flight_time'])

    return head, dict(d)
```

#### Набросаны шаблоны старниц
Сделан минимальный набор шагов (выбор даты - выбор времени - выбор тарифа - переход на страницу оплаты)
и (выбор доступных сертификатов - переход на страницу оплаты)

##### Выбор даты полета
Необходимо было отобразить календарь с доступными датами и возможностью выбора месяца
Даты получаем через SOAP-сервис, вызывая метод `getAvailableDates`, 


#### В зачаточном состоянии rest api
Позволяет получать список пользователей, а также добоавлять

#### Разработан калькулятор на Javascript
Сделан калькулятор на странице для расчета стоимости по полученным тарифам

## Что в планах
#### Тесты и CD
В том числе использовать [Sentry](https://sentry.io)
* [The Django integration](https://docs.sentry.io/platforms/python/django/)
* https://simonwillison.net/2017/Oct/17/free-continuous-deployment/

#### Добавить кэширования результатов запросов API используя [Redis](https://redis.io)
В связи с большим откликом есть необходимость кэшировать полученные данные по доступным датам, количеству свободных минут и тарифам.

Инвалидировать кэш должна инфомационная система комплекса используя rest api веб-приложения django при создании и обновлении(и переносе) полетных записей.

Возможно понадобится использовать redis как очередь сообщений.

* [Список клиентов для python](https://redis.io/clients#python)
* [Github рекомендуемого клиента](https://github.com/andymccurdy/redis-py)
* [Статья по работе с redis в django](https://stackabuse.com/working-with-redis-in-python-with-django/)


#### Доделать rest api для возможности получения данных клиента
Принято решение, что синхронизация пользователей будет происходить по мере необходимости:
1. При регистрации пользователя в веб-приложении его данные в ИС не нужны 
2. При вызове метода веб-сервиса createOrder ИС будет через rest api получать данные пользователя по id
3. При создании пользователя в ИС необходимо проверять наличие данные в веб-приложении по номеру телефона
4. При обновлении данных пользователя в ИС необходимо их обновлять в веб-приложении по id
5. Регламентно (по расписанию) получать список зарегистрированных пользователей

Необходимо добавить в rest api 
* Обновление данных пользователя в веб-приложении
* Получение данных пользователя по номеру телефона
* Получение списка всех пользователей (с пагинацией)

#### Подключить платежную систему
* Yandex money
* Robokassa
+ Веб-хук для подтверждения оплаты


#### Доделать личный кабинет
* Форма регистрации, входа
* Список активированных сертификатов (добавить метод активации подарочного сертификата пользователем)
* Оплаченные заказы
* Данные о предстоящих/проведенных полетах
* Данные по депозиту

#### Генерация электронного сертификата
Создание pdf и отправка на электронную почту клиента.
Все это можно возложить на Celery, так говорят.
* [Introduction to Celery on youtube](https://www.youtube.com/watch?v=3cyq5DHjymw)
* https://devchecklists.com/celery-tasks-checklist/
* https://denibertovic.com/posts/celery-best-practices/

Если только телефон, то генерировать ссылку и отправлять в смс.


#### Сделать бэкэнд для отправки сообщений в [django-sendsms](https://github.com/stefanfoulis/django-sendsms) 
* [Руководство по BYTEHAND API v2](https://www.bytehand.com/ru/developers/v2)
<details><summary>Примитивный пример отправки сообщений на php (открывается по клику)</summary>
<p>

``` php
    <?php
	namespace common\sms;
	use Yii;

	class Bytehand{
		public static function smsSend($phone, $text){
			$params = [
				'id' => \Yii::$app->params['bytehand_id'],
				'key' => \Yii::$app->params['bytehand_key'],
				'from' => \Yii::$app->params['bytehand_from']
			];
			$result = file_get_contents('http://bytehand.com:3800/send?id='. $params['id'] .'&key='. $params['key'] .'&to='.urlencode($phone).'&from='.urlencode($params['from']).'&text='.urlencode($text));
			if($result === false){
			}
		}
	}
    ?>
```

</p>
</details>

#### Ajax

### Материалы, используемые при создании приложения

##### JAVASCRIPT, JQuery
* https://habr.com/ru/post/38208/
* https://www.w3schools.com/js/default.asp
* https://www.w3schools.com/jquery/default.asp

##### BOOTSTRAP
* https://getbootstrap.com/docs/4.4/getting-started/introduction/
* https://www.w3schools.com/bootstrap4/default.asp

##### DJANGO TUTORIALS
* [Django 3.0 docs in PDF](https://buildmedia.readthedocs.org/media/pdf/django/3.0.x/django.pdf)
* [Django (3.0) Crash Course Tutorials - Dennis Ivy on youtube](https://www.youtube.com/watch?v=gXGQmt_U9Ao&list=PL-51WBLyFTg2vW-_6XBoUpE7vpmoR3ztO&index=16)
* [Django Weather App - Pretty Printed on youtube](https://www.youtube.com/watch?v=oPuYTGyW4dU)
* [Creating a Custom User Model (Django) -  CodingWithMitch on youtube](https://www.youtube.com/watch?v=eCeRC7E8Z7Y)

