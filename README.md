# Distributed_TDMA
## Distributed TDMA for Mobile UWB Network Localization

Many applications related to the Internet-of-Things, such as tracking people or objects, robotics, and monitoring require localization of large networks of devices in dynamic, GPS-denied environments. Ultra-WideBand (UWB) technology is a common choice because of its precise ranging capability. However, allowing access and effective use of the shared UWB medium with a constantly changing set of devices faces some particular challenges: high frequency of ranging measurements by the devices to improve system accuracy; network topology changes requiring rapid adaptation; and decentralized operation to avoid single points of failure.

In this paper, we propose a novel Time Division Multiple Access (TDMA) algorithm that can quickly schedule the use of the UWB medium by a large network of devices without collisions in local network neighborhoods and avoiding conflicts with hidden terminals, all the while maximizing network usage. % More importantly, the channel time slots are always completely occupied % by a two-hop neighborhood, which means the time slot reuse rate % through the network is higher. Using exclusively the UWB radio network, we realize a decentralized system for synchronization, dynamic TDMA scheduling, and precise relative positioning on a multi-hop network. Our system does not have special nodes (all nodes are equal) and it is sufficiently scalable for real-world applications. Our method can be applied to implement device localization services in large spaces without GPS and complex topologies, like malls, museums, mines, etc. We demonstrate our method in simulation and on real hardware in an underground parking lot, showing the effectiveness of its TDMA schedule for relative localization.



**Related Paper**

* **Distributed TDMA for Mobile UWB Network Localization**, Cao Y, Chen C, St-Onge D, et al. Distributed TDMA for mobile UWB network localization[J]. IEEE Internet of Things Journal, 2021 (https://ieeexplore.ieee.org/document/9380309)