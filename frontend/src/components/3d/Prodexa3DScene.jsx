import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Text, MeshTransmissionMaterial } from '@react-three/drei';
import * as THREE from 'three';

// Physical 3D Data Object Floating in Space
const PhysicalDataObject = ({ position, label, scrollProgress, speed = 1 }) => {
  const groupRef = useRef();

  useFrame((state, delta) => {
    if (!groupRef.current) return;

    // Movement toward center origin (0,0,0) as scroll progresses (0 -> 1)
    const factor = Math.max(0.1, 1 - scrollProgress * 2.5);
    groupRef.current.position.x = position[0] * factor;
    groupRef.current.position.y = position[1] * factor;
    groupRef.current.position.z = position[2] * factor;

    groupRef.current.rotation.x += delta * 0.4 * speed;
    groupRef.current.rotation.y += delta * 0.5 * speed;
  });

  return (
    <group ref={groupRef}>
      <mesh>
        <boxGeometry args={[0.8, 0.5, 0.25]} />
        <meshPhysicalMaterial
          color="#0F172A"
          roughness={0.1}
          metalness={0.9}
          clearcoat={1}
          clearcoatRoughness={0.1}
        />
      </mesh>
      <mesh>
        <boxGeometry args={[0.82, 0.52, 0.27]} />
        <meshBasicMaterial color="#06B6D4" wireframe />
      </mesh>
      <Text
        position={[0, 0, 0.16]}
        fontSize={0.13}
        color="#F8FAFC"
        font="https://fonts.gstatic.com/s/jetbrainsmono/v18/tT6vB32aC0a6N6m3T9Kz9K9g.woff"
      >
        {label}
      </Text>
    </group>
  );
};

// Sophisticated Multi-Layered Glass Intelligence Core
const SophisticatedCore = ({ scrollProgress }) => {
  const coreGroup = useRef();
  const ring1 = useRef();
  const ring2 = useRef();
  const ring3 = useRef();

  useFrame((state, delta) => {
    if (!coreGroup.current) return;
    coreGroup.current.rotation.y += delta * 0.3;
    if (ring1.current) ring1.current.rotation.x += delta * 0.5;
    if (ring2.current) ring2.current.rotation.y += delta * 0.7;
    if (ring3.current) ring3.current.rotation.z += delta * 0.9;

    const scale = Math.min(1.5, 0.8 + scrollProgress * 1.2);
    coreGroup.current.scale.set(scale, scale, scale);
  });

  return (
    <group ref={coreGroup} position={[0, 0, 0]}>
      {/* Outer Cyan Emissive Ring */}
      <mesh ref={ring1}>
        <torusGeometry args={[2.2, 0.05, 16, 100]} />
        <meshStandardMaterial color="#06B6D4" emissive="#06B6D4" emissiveIntensity={1.2} />
      </mesh>

      {/* Middle Emerald Emissive Ring */}
      <mesh ref={ring2}>
        <torusGeometry args={[1.7, 0.04, 16, 100]} />
        <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={1.2} />
      </mesh>

      {/* Inner Amber Emissive Ring */}
      <mesh ref={ring3}>
        <torusGeometry args={[1.2, 0.03, 16, 100]} />
        <meshStandardMaterial color="#F59E0B" emissive="#F59E0B" emissiveIntensity={1.0} />
      </mesh>

      {/* Layered Transparent Glass Core Sphere */}
      <mesh>
        <sphereGeometry args={[0.75, 32, 32]} />
        <meshStandardMaterial color="#080C14" roughness={0.05} metalness={0.95} />
      </mesh>
      <mesh>
        <sphereGeometry args={[0.78, 16, 16]} />
        <meshBasicMaterial color="#06B6D4" wireframe />
      </mesh>
    </group>
  );
};

// Camera Controller
const CameraRig = ({ scrollProgress }) => {
  useFrame((state) => {
    const targetZ = 7 - scrollProgress * 3;
    const targetY = (scrollProgress - 0.5) * 1.8;
    state.camera.position.z += (targetZ - state.camera.position.z) * 0.05;
    state.camera.position.y += (targetY - state.camera.position.y) * 0.05;
    state.camera.lookAt(0, 0, 0);
  });
  return null;
};

export const Prodexa3DScene = ({ scrollProgress = 0 }) => {
  const dataObjects = [
    { label: 'PDF', pos: [-4.5, 3.2, 2], speed: 0.8 },
    { label: 'CSV', pos: [4.5, 2.8, -1.5], speed: 1.1 },
    { label: 'MPN', pos: [-3.8, -2.8, 1.8], speed: 0.9 },
    { label: 'CATALOG', pos: [3.8, -3.2, -2.2], speed: 1.2 },
    { label: 'SPEC', pos: [-2.5, 3.8, -1.8], speed: 1.0 },
    { label: 'MATERIAL', pos: [2.8, 3.5, 1.2], speed: 0.7 },
    { label: 'MANUFACTURER', pos: [-4.8, 0.8, -2.5], speed: 1.3 },
    { label: 'UOM', pos: [4.8, -0.8, 2.2], speed: 0.9 }
  ];

  return (
    <div className="w-full h-full min-h-[500px]">
      <Canvas camera={{ position: [0, 0, 7], fov: 48 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#06B6D4" />
        <pointLight position={[-10, -10, -10]} intensity={1.0} color="#10B981" />

        <CameraRig scrollProgress={scrollProgress} />
        <SophisticatedCore scrollProgress={scrollProgress} />

        {dataObjects.map((obj, idx) => (
          <PhysicalDataObject
            key={idx}
            position={obj.pos}
            label={obj.label}
            scrollProgress={scrollProgress}
            speed={obj.speed}
          />
        ))}
      </Canvas>
    </div>
  );
};
