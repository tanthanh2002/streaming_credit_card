from confluent_kafka import Consumer, KafkaException
import pandas as pd
import json

consumer_conf = {
 'bootstrap.servers': 'localhost:9092', # Địa chỉ Kafka broker
 'group.id': 'my-group',
 'auto.offset.reset': 'earliest' # Đọc từ đầu
}
# Khởi tạo consumer
consumer = Consumer(consumer_conf)

if __name__ == "__main__":
    topic = 'credit_card'

    consumer.subscribe([topic])
 
    try:
        while True:
                msg = consumer.poll(1000) 
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        continue
                    else:
                        print(f"Lỗi khi đọc tin nhắn: {msg.error()}")
                        break

                # Chuyển đổi giá trị của tin nhắn từ JSON thành DataFrame
                json_data = json.loads(msg.value())
                print(json_data)
    except KeyboardInterrupt:
            pass
    finally:
        consumer.close()

    
