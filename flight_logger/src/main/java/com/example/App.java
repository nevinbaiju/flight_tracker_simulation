package com.example;

import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.json.JSONException;
import org.json.JSONObject;

import redis.clients.jedis.Jedis;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args )
    {
        // Kafka consumer configurations
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092,kafka:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "kafka-consumer-group");
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());

        // Create a Kafka consumer
        Consumer<String, String> consumer = new KafkaConsumer<>(props);

        // Kafka topic to consume messages from
        String topic = "flight_sim";

        // Subscribe to the topic
        consumer.subscribe(Collections.singleton(topic));
        System.out.println("Reading stuff");

        String redisHost = System.getenv("REDIS_HOST");
        int redisPort = Integer.parseInt(System.getenv("REDIS_PORT"));
        String redisPassword = System.getenv("REDIS_PASSWORD");
        try {
            try (Jedis jedis = new Jedis(redisHost, redisPort)) {
                jedis.auth(redisPassword);
                while (true) {
                    // Poll for new messages
                    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                    for (ConsumerRecord<String, String> record : records) {
                        String flightLocation = record.value();
                        JSONObject flightLocationJSON = new JSONObject(flightLocation);
                        String flightId = flightLocationJSON.getString("flight_id");
                        flightLocationJSON.remove("flight_id");
                        
                        jedis.setex(flightId, 15, flightLocationJSON.toString());
                    }
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        } finally {
            consumer.close();
        }
    }
}
